# # app/main.py
from random import randint, random
import token
from fastapi import APIRouter, FastAPI, Depends, Request, Form,HTTPException,Query, Response,Security,BackgroundTasks,Header
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from jose import JWTError
from app.database import get_db, engine,redis_client
from sqlalchemy.orm import Session
from app.models import Base, User,Role,Permission, UserRole,RolePermission
from pydantic import BaseModel, EmailStr
from .crud import save_user ,get_user_by_username# Make sure this function is defined in your crud module
from .hashing import hash_password,verify_password # type: ignore # Ensure you have this function for password hashing
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from flask_cors import CORS
from datetime import datetime, timedelta
from . import models, crud, hashing, jwt,schema
from . import models, crud, hashing, schema
import smtplib
from fastapi import Request, Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from .schema import PermissionRoleCreate
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import uuid
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext  
from .mail import send_email
from .jwt import *
from pathlib import Path
import os
import redis.asyncio as redis
# import requests

from fastapi import HTTPException

app = FastAPI()


# CORS(app) 


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # or specify frontend domain like ["http://localhost:3000"]
    allow_credentials=True,  # Ensure credentials are allowed
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
   
)



# templates = Jinja2Templates(directory="templates")  # Adjust the path if necessary
app.mount("/static", StaticFiles(directory=Path(__file__).parent.parent / "static"), name="static")
app.mount("/static", StaticFiles(directory="static"), name="static")

# app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))
# 
# Create the database tables
Base.metadata.create_all(bind=engine)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Define protected route
from fastapi import APIRouter, Depends

router = APIRouter()

async def validate_token(Authorize: AuthJWT = Depends()):
    try:
        # Validate the token using FastAPI-JWT-Auth
        Authorize.jwt_required()
        token_subject = Authorize.get_jwt_subject()

        # Construct the Redis key based on the token subject (e.g., username)
        redis_key = f"token:{token_subject}"
        
        # Check if the token exists in Redis
        if not redis_client.exists(redis_key):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token"
            )
        
        # Optionally return the subject for further use
        return token_subject
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token validation failed"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )

@router.get("/protected-route")
async def protected_route(
    username: str = Depends(validate_token),
    db: Session = Depends(get_db)
):
    # Use the `username` returned by validate_token
    return {"message": f"Welcome, {username}!"}
# _______________________________________________________________________________________________________________#
### otp generate
def otp(n):
    return ''.join(str(randint(0, 9)) for _ in range(n))
#_______________________________________________________________________________________________________________#
##  login


@app.get("/", response_class= HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login/",response_class= HTMLResponse)
def login(
    response: Response,
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):


    if redis_client.exists(f"access_token:{username}"):
        raise HTTPException(status_code=400, detail="User already logged in")


    db_user = db.query(User).filter(User.username == username).first()
    
    # Check if db_user exists
    if not db_user:
        raise HTTPException(status_code=400, detail="User not found")
    
    # user_email = db_user.email 

    # Verify password (replace with your hashing logic)
    if not hashing.verify_password(password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    # Access the user_role
    user_role = db.query(UserRole).filter(UserRole.user_id == db_user.id).first()

    if not user_role:
        raise HTTPException(status_code=400, detail="User role not found")

    role = db.query(Role).filter(Role.id == user_role.role_id).first()

    if not role:
        raise HTTPException(status_code=400, detail="Role not found")

    # Create the JWT token
    
    access_token = Authorize.create_access_token(subject=db_user.username)
    expiration_time = timedelta(hours=1)
    # Store refresh token in Redis with expiration
    redis_client.set(f"access_token:{username}",access_token,ex=expiration_time)
   
    # send_email(user_email, f"Login successfull username: {username}")
    
    redirect_url = (
        "/admin" if role.role_name == "admin" 
        else "/SuperAdminDeshbord" if role.role_name == "SuperAdmin" 
        else "/Udeshbord"
    )

    # Return redirect URL and token
    return JSONResponse(
        status_code=200,
        content={
            "redirect_url": redirect_url,
            "access_token": access_token,
            "username": username
        },
    )
    
    
    





# _______________________


@app.post("/logout/")
async def logout(Authorize: AuthJWT = Depends()):
    try:
        # Get the username of the current logged-in user from the JWT
        current_user = Authorize.get_jwt_subject()
        
        if not current_user:
            raise HTTPException(status_code=400, detail="User not logged in")
        
        # Remove the user's access token from Redis (logging them out)
        redis_client.delete(f"access_token:{current_user}")
        
        return {"message": "Successfully logged out"}
    
    except Exception as e:
        print(f"Error during logout: {e}")
        raise HTTPException(status_code=500, detail="Logout failed")
# Other routes and code..
##______________________________________________________________________________________________________________#



# Create a new permission
@app.post("/permission_create/",response_class= HTMLResponse)
def create_permission(
    request: Request,
    permission_name: str = Form(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)): 
     
    try:  
        Authorize.jwt_required() 
        user = Authorize.get_jwt_subject() 
        print(user)
    except Exception as e:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")    
     
    
    # Check for existing permission
    existing_permission = db.query(Permission).filter(Permission.permission_name == permission_name).first()
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists")

    # Create a new permission
    new_permission = Permission(permission_name=permission_name)
    db.add(new_permission)
    
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")

    db.refresh(new_permission) 
    return JSONResponse(content={"message": "Permission created successfully"})


    # return  "Permission created successfully"
    # return templates.TemplateResponse("add_permission.html",
    # {    
    #     "request": request,
    #     "msg": "Permission created successfully",
    #     "permission_id": new_permission.id,
    #     "permission_name": new_permission.permission_name
    # })


#____________________delete permission api___________________


@app.delete("/permission_delete/{permission_id}")
def delete_permission(permission_id: int, Authorize: AuthJWT = Depends(), db: Session = Depends(get_db)):
    try:
        Authorize.jwt_required()
        user = Authorize.get_jwt_subject()
        print(user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    permission = db.query(Permission).filter(Permission.id == permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    db.delete(permission)
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return {"detail": "Permission deleted successfully"}

# ______________________________________________________________________________________________________________________________
# Create a new role # Role Table
#____GetAll Roles 

@app.get("/SuperAdmin_get_roles")
def get_roles(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()  # Get the current logged-in user

    # Fetch the user and their role in a single query
    user_with_role = (
        db.query(User, Role)
        .join(UserRole, User.id == UserRole.user_id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(User.username == current_user)
        .first()
    )

    if not user_with_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or role not found")

    user, role = user_with_role
    
    # Check if the user has 'superadmin' role
    if role.role_name == "SuperAdmin":
        # Fetch all roles excluding 'superadmin'
        roles = db.query(Role).filter(Role.role_name != "SuperAdmin").all()
        return [{"id": role.id, "role_name": role.role_name} for role in roles]
    
    roles = db.query(Role).filter(Role.role_name != "admin" , Role.role_name != "SuperAdmin").all()
    return [{"id": role.id, "role_name": role.role_name} for role in roles]

 
#super Admin delete role dropedown

@app.post("/roles_create/",response_class= HTMLResponse)
def create_role(
    request: Request ,
    role_name: str = Form(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)): 
    
    try: 
       Authorize.jwt_required()  
       user = Authorize.get_jwt_subject() 
    except Exception as e:
        print("exception")
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")    
     
    # Check for existing role
    existing_role = db.query(Role).filter(Role.role_name == role_name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role already exists")

    new_role = Role(role_name=role_name)
    db.add(new_role) 
    db.commit()
    db.refresh(new_role)
    return JSONResponse(content={"message": "Role created successfully"})

    # return "Role created successfully"
    # return templates.TemplateResponse("AddRole.html",
    # {
    # "request": request,
    # "role_id": new_role.id,
    # "role_name": new_role.role_name })
    


 #delete role 
@app.post("/roles_delete", response_class=HTMLResponse)
def delete_role(
    request: Request,
    role_name: str = Form(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db)):
    
    try: 
        Authorize.jwt_required()  
        user = Authorize.get_jwt_subject() 
        print(user)
    except Exception as e:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")    
     
    # Check if the role exists
    role = db.query(Role).filter(Role.role_name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Delete the role
    db.delete(role)
    db.commit()
    return JSONResponse(content={"message": "Role deleted successfully"})

    # return "Role deleted successfully"
    # Optionally, redirect back to a role management page
    # return templates.TemplateResponse("AddRole.html", {"role_name": role_name,"request": request, "msg": "Role deleted successfully"})
   
# #______________________________________________________________________________________________________________#
    


@app.post("/user_role/", response_class=HTMLResponse)
def create_user_role(
    request: Request, 
    username: str = Form(...),  # Explicitly expect 'username' as form data
    role_name: str = Form(...),  # Explicitly expect 'role_name' as form data
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    # Fetch the user from the database based on the username
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Fetch the role from the database based on the role_name
    role = db.query(Role).filter(Role.role_name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Check if the UserRole already exists
    existing_user_role = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role_id == role.id
    ).first()
    if existing_user_role:
        raise HTTPException(status_code=400, detail="UserRole already exists")

    # Create the new UserRole
    new_user_role = UserRole(user_id=user.id, role_id=role.id)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return JSONResponse(content={"message": "user role asign successfully"})

    # return "user role asign successfully"

    # return templates.TemplateResponse(
    #     "useroleDrop.html",
    #     {
    #         "request": request,
    #         "username": user.username,  # Correctly pass the username here
    #         "user_role_id": new_user_role.id,
    #     }
    # )
    
#______________________________________________________________________________________________________________#  


@app.get("/get_permissions")
def get_permissions(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()  # Ensure the request contains a valid JWT
    permissions = db.query(Permission).all()  # Fetch all permissions
    return [{"id": perm.id, "permission_name": perm.permission_name} for perm in permissions]



#### roles permision table
@app.post("/permission_roles_create/",response_class= HTMLResponse)
def create_permission_role(
    request: Request, 
    permission_role: PermissionRoleCreate,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    # Check if the role exists
    role = db.query(Role).filter(Role.role_name == permission_role.role_name).first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    created_permission_roles = []

    # Iterate through the permission names from the request
    for permission_name in permission_role.permission_names:
        # Check if each permission exists
        permission = db.query(Permission).filter(Permission.permission_name == permission_name).first()
        
        if not permission:
            raise HTTPException(status_code=404, detail=f"Permission '{permission_name}' not found")

        # Create a new role-permission association
        role_permission = RolePermission(permission_id=permission.id, role_id=role.id)
        db.add(role_permission)
        
        # Append the new role_permission to the list of created_permission_roles
        created_permission_roles.append(role_permission)

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database error")
    
    return JSONResponse(content={"message": "Permission asign to the Role Successfully"})

    # return "Permission asign to the Role Successfully"

    # return templates.TemplateResponse("per_role.html",
    # {'request':request,"permission_role_ids": [print(rp.id) for rp in created_permission_roles]})
   


#______________________________________________________________________________________________________________#

# User Dashbord
@app.get("/Udeshbord_ren", response_class=HTMLResponse)
def user_dashboard(request: Request, db: Session = Depends(get_db),Authorize: AuthJWT = Depends()): 
    
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
        current_user_id = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    user = db.query(User).filter(User.username == current_user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()

    if not user_roles:
        raise HTTPException(status_code=404, detail="No roles found for this user")

    roles = []
    permissions = set()
    response=[]
    for user_role in user_roles:
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        if role:
            roles.append(role.role_name)

            role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
            for role_permission in role_permissions:
                permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
                if permission:
                    permissions.add(permission.permission_name)

    response.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": roles,
            "permissions": list(permissions)
        })
    return JSONResponse(content={"users_data": response})
#_________________________________________________________________________#
##admin deshbord

@app.get("/Admin_Deshbord", response_class=HTMLResponse)
  # Protect this route with JWT authorization
def admin_deshbord(
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()  # Inject the AuthJWT dependency
):
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
        current_user = Authorize.get_jwt_subject()
        print(current_user)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    
    # Retrieve all users
    users = db.query(User).all()
    response = []

    for user in users:
        # Get roles associated with the user
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
        roles = []
        permissions = set()  # Use a set to avoid duplicates
        is_superadmin = False
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append(role.role_name)
                if role.role_name == "SuperAdmin" or role.role_name == "admin" :  # Check if the role is 'SuperAdmin'
                  is_superadmin = True 

                # Get permissions for this role
                role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
                for role_permission in role_permissions:
                    permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
                    if permission:
                        permissions.add(permission.permission_name)
        
        # Append user information to the response list
        if is_superadmin:
          continue
        response.append(
            {
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": roles,
            "permissions": list(permissions)
        }) 
        return JSONResponse(content={"users_data": response})
              
    # Return the template response with the users data
    # return templates.TemplateResponse("AdminDeshbord.html", {"request": request, "users_data": response})
    
    
    

#super admin deshbord ______________________________________________
@app.get("/SuperAdminDeshbord_change", response_class=HTMLResponse)
def Superadmin_deshbord(
    request: Request,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),# Inject the AuthJWT dependency
):
    Authorize.jwt_required()
    username = Authorize.get_jwt_subject()
    print(f'current username {username}')
   
    # Retrieve all users
    users = db.query(User).all()

    # Prepare a response list
    response = []

    for user in users:
        # Get roles associated with the user
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
        roles = []
        permissions = set()  # Use a set to avoid duplicates
        is_superadmin = False
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append(role.role_name)
                if role.role_name == "SuperAdmin":  # Check if the role is 'SuperAdmin'
                  is_superadmin = True 

                # Get permissions for this role
                role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
                for role_permission in role_permissions:
                    permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
                    if permission:
                        permissions.add(permission.permission_name)
        
        if is_superadmin:
          continue
        # Append user information to the response list
        response.append({
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "roles": roles,
            "permissions": list(permissions)
        })
    return JSONResponse(content={"users_data": response})
    # Return the template response with the users data
    # return templates.TemplateResponse("SuperAdmin.html", {"request": request, "users_data": response})
    
#______________________________________________________________________________________________________________#


# itself update api SuperAdmin , Admin And All the Users  update 
@app.post("/UpdateItSelf/")
async def updateItself(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    
    # Fixing the query to filter by either username or email
    existing_user = db.query(User).filter(User.username == current_user).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Fetching the user with role
    user_with_role = (
        db.query(User, Role)
        .join(UserRole, User.id == UserRole.user_id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(User.username == current_user)
        .first()
    )

    if not user_with_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or role not found")

    # Update user details
    existing_user.username = username
    existing_user.email = email

    # Commit changes to the database
    db.commit()
    
    # Refresh the user to get updated details
    db.refresh(existing_user)

    user, role = user_with_role

    redirect_url = (
        "/admin" if role.role_name == "admin" 
        else "/SuperAdminDeshbord" if role.role_name == "SuperAdmin" 
        else "/Udeshbord"
    )

    # Return redirect URL and token
    return JSONResponse(
        status_code=200,
        content={
            "redirect_url": redirect_url,
            "updated_user": {
                "username": existing_user.username,
                "email": existing_user.email,
            },
        },
    )
    

# ___________________________________

    
######---work with both superadmin and admin
@app.post("/admin_update/{user_id}", response_class=HTMLResponse)
async def update_user(
    user_id: int,
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    role: str = Form(...),
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    print(f"Received request to update user with user_id={user_id}, username={username}, email={email}, role={role}")

    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token"
        )

    # Find the user by `user_id`
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update the user's information
    if username:
        user.username = username
    if email:
        user.email = email

    # Update role logic
    if role:
        # Find the role instance
        role_instance = db.query(Role).filter(Role.role_name == role).first()
        if not role_instance:
            raise HTTPException(status_code=400, detail="Role does not exist")

        # Update or create UserRole
        user_role_instance = db.query(UserRole).filter(UserRole.user_id == user.id).first()
        if user_role_instance:
            user_role_instance.role_id = role_instance.id
        else:
            # Add a new UserRole if none exists
            new_user_role = UserRole(user_id=user.id, role_id=role_instance.id)
            db.add(new_user_role)

    # Commit changes
    db.commit()
    db.refresh(user)
    
    # return "User Update Successfully"
    return JSONResponse(content={"message": "User updated successfully"})

    # Render the update.html template with updated user details and available roles
    # return templates.TemplateResponse(
    #     "update.html",
    #     {"request": request, "username": user.username, "email": user.email, "roles": role},
    # )
  



#____________________________________________________________________________________________________________________#

    
from .render import *


@app.get("/users_delete/{username}")
async def delete_user(
    request: Request,
    username: str,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        Authorize.jwt_required()  # Ensure the request contains a valid JWT
        current_user = Authorize.get_jwt_subject()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")

    # Ensure the user is allowed to delete the target user account (either admin or the user themselves)
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_role = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    for role in user_role:
        db.delete(role)
    # Delete the user
    db.delete(user)
    db.commit()
    return{"username delete succesfully"}

#______________________________________________________________________________________________________________#
@app.get("/forget-password/",response_class= HTMLResponse)
async def forget_password(request: Request,Authorize: AuthJWT = Depends()):
    return templates.TemplateResponse("forgot.html", {"request": request})


@app.post("/forgot_pass/", response_class=HTMLResponse)
async def forget(
    request: Request,
    email: EmailStr = Form(...), 
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
 
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Generate a 6-digit OTP
    verification_code = otp(6)

    # Store the OTP in Redis with a 5-minute expiration time (300 seconds)
    redis_client.setex("otp:email", 10000, verification_code)

    # Send OTP to the user's email asynchronously
    send_email(email, verification_code)

    # Return the OTP entry form where the user can enter the OTP
    return templates.TemplateResponse(
        "ForgotOtp.html",  # Ensure this template exists
        {"request": request, "email": email}
    )

#----------------------    


@app.post("/verifOpt/", response_class=HTMLResponse)
async def verify_otp_pass(
    request: Request,
    otp: str = Form(...),  # OTP entered by the user
    email: EmailStr = Form(...),  # Email address of the user
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    
    """Verify OTP and allow user to reset password if valid"""
    
    # Retrieve the OTP from Redis
    stored_otp = redis_client.get("otp:email")
    print(stored_otp)
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP has expired or does not exist")
    stored_otp = stored_otp.decode("utf-8")
    print(stored_otp)
    # Compare the entered OTP with the stored OTP
    if otp !=  stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    
    delete=redis_client.delete("otp:email")
    print(delete)
    # OTP is valid, proceed to show the reset password form
    return templates.TemplateResponse(
        "resetPassword.html",  # Ensure this template exists
        {"request": request, "email": email}
    )


#-----------------
@app.post("/resetpassword/" ,response_class= HTMLResponse)
async def reset_password(
    request:Request,
    email: EmailStr = Form(...),
    new_password: str= Form(...),
    confirm_password: str= Form(...),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
    ):

    print("check")
    user = db.query(User).filter(User.email == email).first()
    print("email")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    print("con")
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user.password = hash_password(new_password)  # Hash the new password
    user.reset_token = None  # Clear the token
    db.commit()
    
    return RedirectResponse(url="/", status_code=303)





#--------------------------------------------------


from fastapi.responses import JSONResponse

@app.post("/change-password/", response_class=JSONResponse)
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends()
):
    try:
        # Ensure the request contains a valid JWT
        Authorize.jwt_required()  
        current_user = Authorize.get_jwt_subject()  # Extract the current user's email (subject from the token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token")
    
    # Fetch the user based on the email obtained from the token (current_user_email)
    user = db.query(User).filter(User.username == current_user).first()  # Use email to query the user
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user_email = user.email 
    # Verify the old password (compare the hash of the old password)
    if not verify_password(old_password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect old password")
    
    # Ensure the new password is different from the old password
    if old_password == new_password:
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")
    
    # Ensure the new password matches the confirmed password
    if new_password != confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
    
    # Hash the new password before updating
    hashed_new_password = hash_password(new_password)
    
    # Update the user's password in the database
    user.password = hashed_new_password
    db.commit()
    send_email(user_email, f"change password successfull and your password is: {new_password}")
    # Return JSON response with success message
    return JSONResponse(content={"msg": "Password has been changed successfully."})

# #####-----------------------

# #_____________________________________________Users Handler Code___________________________________________________________________#


import redis 
@app.get("/check-redis")
def check_redis():
    try:
        # Testing if Redis is responsive
        if redis_client.ping():
            return {"status": "success", "message": "Redis is connected"}
    except redis.ConnectionError:
        raise HTTPException(status_code=500, detail="Could not connect to Redis")
    
    
##########################  Admin Signup page ###################
@app.get("/signup/", response_class= HTMLResponse)
def AdminSignup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

   
@app.post("/admin-signup/", response_class=HTMLResponse ,name="AdminSignup")
async def admin_signup(
    response: Response,
    request: Request,
    background_tasks: BackgroundTasks,
    username: str = Form(...),  # Form data for username
    email: str = Form(...),  # Form data for email
    password: str = Form(...),  # Form data for password
    db: Session = Depends(get_db),  # Database session
):
    # Check if the email or username is already in use
    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Generate a 6-digit OTP for email verification
    verification_code = otp(6)
    
    # Store the OTP in Redis with a 5-minute expiration time (300 seconds)
    redis_client.setex(f"otp:{email}", 300, verification_code)

    # Send the OTP to the user's email asynchronously
    background_tasks.add_task(send_email, email, verification_code)

    # Return the OTP verification page (email is passed as a hidden field)
    return templates.TemplateResponse(
        "verify_otp.html",  # This template should have a form to enter the OTP
        {"request": request, "email": email, "username": username, "password": password}
    )


@app.post("/verifyOTP/", response_class=HTMLResponse)
async def verify_otp(
    request: Request,
    # background_tasks: BackgroundTasks,
    otp: str = Form(...),  # OTP entered by the user
    email: str = Form(...),  # Email address of the user
    username: str = Form(...),  # Username of the user
    password: str = Form(...),  # Password of the user
    db: Session = Depends(get_db),  # Database session
      # Background tasks for sending confirmation email
):
    print(f"Received OTP: {otp}, Email: {email}, Username: {username}, Password: {password}")
    # Retrieve the OTP from Redis
    stored_otp = redis_client.get(f"otp:{email}")

    print(stored_otp)
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP has expired or does not exist")

    stored_otp = stored_otp.decode("utf-8")
    if otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Check if the "admin" role exists in the database
    admin_role = db.query(Role).filter(Role.role_name == "admin").first()

    if not admin_role:
        # If the "admin" role doesn't exist, create it
        admin_role = Role(role_name="admin")
        db.add(admin_role)
        db.commit()
        db.refresh(admin_role)

    # Create the new user and mark them as verified (since OTP is valid)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_verified=True  # Mark the user as verified after OTP
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create the UserRole entry to associate the new user with the "admin" role
    user_role = UserRole(user_id=new_user.id, role_id=admin_role.id)
    db.add(user_role)
    db.commit()

    # Optionally send a confirmation email saying the verification was successful
    # background_tasks.add_task(send_email, email, "Your account has been verified successfully!")

    # Return a success message or redirect to the login page
    return templates.TemplateResponse(
        "verification_success.html",  # A success page after OTP verification
        {"request": request,"message": "Your account has been successfully verified!"}
    )



##########################  User Signup page ###################

@app.post("/user-signup/", response_class=HTMLResponse,name="UserSignup")
async def user_signup(
    response: Response,
    request: Request,
    background_tasks: BackgroundTasks,
    username: str = Form(...),  # Form data for username
    email: str = Form(...),  # Form data for email
    password: str = Form(...),  # Form data for password
    db: Session = Depends(get_db),  # Database session
):
    # Check if the email or username is already in use
    existing_user = db.query(User).filter((User.email == email) | (User.username == username)).first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Email or username already registered")
    
    # Generate a 6-digit OTP for email verification
    verification_code = otp(6)
    
    # Store the OTP in Redis with a 5-minute expiration time (300 seconds)
    redis_client.setex(f"otp:{email}", 300, verification_code)

    # Send the OTP to the user's email asynchronously
    background_tasks.add_task(send_email, email, verification_code)

    # Return the OTP verification page (email is passed as a hidden field)
    return templates.TemplateResponse(
        "UserOtpVerify.html",  # This template should have a form to enter the OTP
        {"request": request, "email": email, "username": username, "password": password}
    )


@app.post("/UserOTP/", response_class=HTMLResponse)
async def User_otp(
    request: Request,
    # background_tasks: BackgroundTasks,
    otp: str = Form(...),  # OTP entered by the user
    email: str = Form(...),  # Email address of the user
    username: str = Form(...),  # Username of the user
    password: str = Form(...),  # Password of the user
    db: Session = Depends(get_db),  # Database session
      # Background tasks for sending confirmation email
):
    print(f"Received OTP: {otp}, Email: {email}, Username: {username}, Password: {password}")
    # Retrieve the OTP from Redis
    stored_otp = redis_client.get(f"otp:{email}")

    print(stored_otp)
    if not stored_otp:
        raise HTTPException(status_code=400, detail="OTP has expired or does not exist")
    
    stored_otp = stored_otp.decode("utf-8")
    if otp != stored_otp:
        raise HTTPException(status_code=400, detail="Invalid OTP")

    # Hash the password
    hashed_password = pwd_context.hash(password)

    # Check if the "demo" role exists in the database
    user_role = db.query(Role).filter(Role.role_name =="demo").first()
    print(user_role)
    if not user_role:
        # If the "demo" role doesn't exist, create it
        user_role = Role(role_name="demo")
        db.add(user_role)
        db.commit()
        db.refresh(user_role)

    # Create the new user and mark them as verified (since OTP is valid)
    new_user = User(
        username=username,
        email=email,
        password=hashed_password,
        is_verified=True  # Mark the user as verified after OTP
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create the UserRole entry to associate the new user with the "demo" role
    user_role = UserRole(user_id=new_user.id, role_id=user_role.id)
    db.add(user_role)
    db.commit()

    # Optionally send a confirmation email saying the verification was successful
    # background_tasks.add_task(send_email, email, "Your account has been verified successfully!")

    # Return a success message or redirect to the login page
    return templates.TemplateResponse(
        "verification_success.html",  # A success page after OTP verification
        {"request": request,"message": "Your account has been successfully verified!"}
    )



# __________________________________________________________________________________________________________#

# webshockets
from .webshockets import WebSocket,manager,get_all_key_values,json,WebSocketDisconnect ,change_random_value,asyncio

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)  # Add the WebSocket to the manager
    try:
        # Send all available keys to the new client
        all_keys = get_all_key_values()
        key_value_pairs = {key.decode(): value.decode() for key, value in all_keys.items()}
        await manager.send_personal_message(json.dumps(key_value_pairs), websocket)

        while True:
            message = await websocket.receive_text()
            print(f"Received message: {message}")

            # Handle multiple subscriptions (message is expected to be a JSON array)
            if message.startswith("subscribe:"):
                try:
                    # Parse the message content as a JSON array (assuming the format ["key1", "key2"])
                    keys = json.loads(message[len("subscribe:"):].strip())
                    if isinstance(keys, list):
                        manager.subscribe(websocket, set(keys))
                        await manager.send_personal_message(f"Subscribed to keys: {', '.join(keys)}", websocket)
                        print(f"WebSocket subscribed to keys: {keys}")
                    else:
                        await manager.send_personal_message("Invalid subscription format", websocket)
                except json.JSONDecodeError:
                    await manager.send_personal_message("Invalid JSON format for subscription", websocket)
                    print(f"Invalid subscription message received: {message}")
    except WebSocketDisconnect:
        # Remove WebSocket on disconnect
        manager.disconnect(websocket)
        print("Client disconnected")


@app.get("/web", response_class=HTMLResponse)
async def get_web(request: Request):
    return templates.TemplateResponse("web.html", {"request": request})


# ____________________________________________________________________________




from fastapi.responses import StreamingResponse
import io
import csv
from fastapi.responses import FileResponse

# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject() 
#     # Retrieve all users
#     users = db.query(User).all()

#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)
    
#     # Write header to CSV
#     csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

#     for user in users:
#         # Get roles associated with the user
#         user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
#         roles = []
#         permissions = set()  # Use a set to avoid duplicates
#         is_superadmin = False
#         for user_role in user_roles:
#             role = db.query(Role).filter(Role.id == user_role.role_id).first()
#             if role:
#                 roles.append(role.role_name)
#                 if role.role_name == "SuperAdmin":  # Check if the role is 'SuperAdmin'
#                     is_superadmin = True 

#                 # Get permissions for this role
#                 role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
#                 for role_permission in role_permissions:
#                     permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#                     if permission:
#                         permissions.add(permission.permission_name)
        
#         if is_superadmin:
#             continue

#         # Write the user data to the CSV
#         csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_data.csv"})






@app.get("/download_roles_csv")
def download_roles_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()  # Get the current logged-in user
   
    # Fetch the user and their role in a single query
    user_with_role = (
        db.query(User, Role)
        .join(UserRole, User.id == UserRole.user_id)
        .join(Role, Role.id == UserRole.role_id)
        .filter(User.username == current_user)
        .first()
    )

    if not user_with_role:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or role not found")

    user, role = user_with_role

    # Check if the user has 'superadmin' role
    if role.role_name == "SuperAdmin":
        # Fetch all roles excluding 'superadmin'
        roles = db.query(Role).filter(Role.role_name != "SuperAdmin").all()
    elif  role.role_name == "admin":
        # roles = db.query(Role).filter(Role.role_name != "admin", Role.role_name != "SuperAdmin").all()
        roles = db.query(Role).filter( Role.role_name != "SuperAdmin").all()
    else:
        roles = [role]

    
    # Prepare CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write the header to CSV
    csv_writer.writerow(["role_id", "role_name"])

    # Write the role data to CSV
    for role in roles:
        csv_writer.writerow([role.id, role.role_name])

    # Move the pointer to the beginning of the StringIO buffer
    output.seek(0)
    
    file_path = "csv_file/roles.csv"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the content to the file
    with open(file_path, "w", newline="") as f:
        f.write(output.getvalue())
    # Return the CSV file as a downloadable file
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=roles.csv"
    })






# @app.get("/download_permission_csv")
# def download_permission_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):

#     Authorize.jwt_required()  # Ensure the request contains a valid JWT

#     permissions = db.query(Permission).all()  # Fetch all permissions
    
#      # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)

#     # Write the header to CSV
#     csv_writer.writerow(["permission_id", "permission_name"])
    
#     for permission in permissions:
#         csv_writer.writerow([permission.id, permission.permission_name])
#     output.seek(0)

#     return StreamingResponse(output, media_type="text/csv", headers={
#         "Content-Disposition": "attachment; filename=permission.csv"
#     })

# @app.get("/download_permission_csv")
# def download_permission_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     # Ensure the request contains a valid JWT
#     Authorize.jwt_required()

#     # Get the current logged-in user from the JWT token (this is usually the username or user identifier)
#     current_user = Authorize.get_jwt_subject()

#     # Fetch the user object from the database using the username (not user.id)
#     user = db.query(User).filter(User.username == current_user).first()  # Use .first() to get a single user

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Fetch the roles assigned to the current user using user.id (not current_user)
#     user_roles = db.query(UserRole).join(Role).filter(UserRole.user_id == user.id).all()  # Use user.id here

#     # Initialize a set to store unique permissions
#     permissions_set = set()

#     # For each role the user has, fetch the associated permissions
#     for user_role in user_roles:
#         role = user_role.role
        
#         # Fetch permissions associated with the role
#         role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()

#         for role_permission in role_permissions:
#             permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#             if permission:
#                 permissions_set.add(permission)  # Add to the set, duplicates will be automatically handled

#     # Prepare the CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)

#     # Write the header for the CSV file
#     csv_writer.writerow(["permission_id", "permission_name"])

#     # Write each unique permission into the CSV file
#     for permission in permissions_set:
#         csv_writer.writerow([permission.id, permission.permission_name])

#     # Move the pointer to the beginning of the StringIO buffer to prepare for download
#     output.seek(0)

#     # Return the CSV as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={
#         "Content-Disposition": "attachment; filename=permissions.csv"
#     })



# _________using joins_________#

@app.get("/download_permission_csv")
def download_permission_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Ensure the request contains a valid JWT
    Authorize.jwt_required()

    # Get the current logged-in user from the JWT token (this is usually the username or user identifier)
    current_user = Authorize.get_jwt_subject()

    # Fetch the user object from the database using the username (not user.id)
    user = db.query(User).filter(User.username == current_user).first()  # Use .first() to get a single user

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch roles and permissions using SQLAlchemy joins in one query
    permissions = (
        db.query(Permission)
        .join(RolePermission, RolePermission.permission_id == Permission.id)
        .join(Role, Role.id == RolePermission.role_id)
        .join(UserRole, UserRole.role_id == Role.id)
        .filter(UserRole.user_id == user.id)
        .distinct()  # Ensures unique permissions
        .all()
    )
    for per in permissions:
        print(per.id)
      
    # Prepare the CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)

    # Write the header for the CSV file
    csv_writer.writerow(["permission_id", "permission_name"])

    # Write each unique permission into the CSV file
    for permission in permissions:
        csv_writer.writerow([permission.id, permission.permission_name])

    # Move the pointer to the beginning of the StringIO buffer to prepare for download
    output.seek(0)
    
     # Define the file path where you want to save the CSV file
    file_path = "csv_file/permissions.csv"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the content to the file
    with open(file_path, "w", newline="") as f:
        f.write(output.getvalue())

    # Return the CSV as a downloadable file
    return StreamingResponse(output, media_type="text/csv", headers={
        "Content-Disposition": "attachment; filename=permissions.csv"
    })

# _____________________


@app.get("/download_users_csv")
def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    # Ensure the request contains a valid JWT
    Authorize.jwt_required()
    current_user = Authorize.get_jwt_subject()

    # Retrieve the current user from the database
    user = db.query(User).filter(User.username == current_user).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Fetch the roles assigned to the current user
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()

    roles = [role.role_name for user_role in user_roles for role in [db.query(Role).filter(Role.id == user_role.role_id).first()]]
    
    is_superadmin = "SuperAdmin" in roles
    is_admin = "admin" in roles

    # Prepare CSV in memory
    output = io.StringIO()
    csv_writer = csv.writer(output)
    
    # Write header to CSV
    csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

    if is_superadmin:
        # If the current user is SuperAdmin, include all users except SuperAdmin
        users = db.query(User).filter(User.username != "SuperAdmin").all()
    elif is_admin:
        users = db.query(User).filter(User.username != "SuperAdmin").all()
    else:
        # If the current user is not SuperAdmin or Admin, include only the current user's entry
        users = [user]  # Only add the current user's data

    # Iterate over the selected users to add them to the CSV
    for user in users:
        # Get roles associated with the user
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
        roles = []
        permissions = set()  # Use a set to avoid duplicates
        for user_role in user_roles:
            role = db.query(Role).filter(Role.id == user_role.role_id).first()
            if role:
                roles.append(role.role_name)

                # Get permissions for this role
                role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
                for role_permission in role_permissions:
                    permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
                    if permission:
                        permissions.add(permission.permission_name)

        # Write the user data to the CSV
        csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

    # Move the pointer to the beginning of the StringIO buffer
    output.seek(0)

    # Define the file path where you want to save the CSV file
    file_path = "csv_file/users_data.csv"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the content to the file
    with open(file_path, "w", newline="") as f:
        f.write(output.getvalue())

    # Return the file path for download
    return FileResponse(file_path, media_type="text/csv", headers={"Content-Disposition": f"attachment; filename=users_data.csv"})


# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject()

#     # Fetch the current user from the database by username (current_user is usually the username)
#     user = db.query(User).filter(User.username == current_user).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Fetch the roles assigned to the current user
#     user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()

#     roles = [role.role_name for user_role in user_roles for role in [db.query(Role).filter(Role.id == user_role.role_id).first()]]

#     is_superadmin = "SuperAdmin" in roles
#     is_admin = "Admin" in roles

#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)
    
#     # Write header to CSV
#     csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

#     # Get users to include in the CSV based on the current user's role
#     if is_superadmin:
#         # If the current user is SuperAdmin, include all users except SuperAdmin
#         users = db.query(User).filter(User.username != "SuperAdmin").all()
#     elif is_admin:
#         # If the current user is Admin, include all users except SuperAdmin and Admin
#         users = db.query(User).filter(User.username != "SuperAdmin", User.username != "Admin").all()
#     else:
#         # If the current user is not SuperAdmin or Admin, include only the current user's entry
#         users = [user]

#     # Iterate over the selected users to add them to the CSV
#     for user in users:
#         # Get roles associated with the user
#         user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
#         roles = []
#         permissions = set()  # Use a set to avoid duplicates
#         for user_role in user_roles:
#             role = db.query(Role).filter(Role.id == user_role.role_id).first()
#             if role:
#                 roles.append(role.role_name)

#                 # Get permissions for this role
#                 role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
#                 for role_permission in role_permissions:
#                     permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#                     if permission:
#                         permissions.add(permission.permission_name)

#         # Write the user data to the CSV
#         csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_data.csv"})



# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject()

#     # Fetch the current user from the database by username (current_user is usually the username)
#     user = db.query(User).filter(User.username == current_user).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Fetch the roles assigned to the current user
#     user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()

#     roles = [role.role_name for user_role in user_roles for role in [db.query(Role).filter(Role.id == user_role.role_id).first()]]

#     is_superadmin = "SuperAdmin" in roles
#     is_admin = "Admin" in roles
 
#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)
    
#     # Write header to CSV
#     csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

#     # Get users to include in the CSV based on the current user's role
#     if is_superadmin or is_admin:
#         # If the current user is SuperAdmin, include all users except SuperAdmin
#         users = db.query(User).filter(User.username != "SuperAdmin").all()
#     # elif is_admin:
#     #     # If the current user is Admin, include all users except SuperAdmin
#     #     users = db.query(User).filter(User.username != "SuperAdmin").all()
#     else:
#         # If the current user is not SuperAdmin or Admin, include only the current user's entry
#         users = [user]

#     # Iterate over the selected users to add them to the CSV
#     for user in users:
#         # Get roles associated with the user
#         user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
#         roles = []
#         permissions = set()  # Use a set to avoid duplicates
#         for user_role in user_roles:
#             role = db.query(Role).filter(Role.id == user_role.role_id).first()
#             if role:
#                 roles.append(role.role_name)

#                 # Get permissions for this role
#                 role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
#                 for role_permission in role_permissions:
#                     permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#                     if permission:
#                         permissions.add(permission.permission_name)

#         # Write the user data to the CSV
#         csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_data.csv"})



# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject() 
#     # Retrieve all users
#     users = db.query(User).all()

#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)
    
#     # Write header to CSV
#     csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

#     for user in users:
#         # Get roles associated with the user
#         user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
#         roles = []
#         permissions = set()  # Use a set to avoid duplicates
#         is_superadmin = False
#         for user_role in user_roles:
#             role = db.query(Role).filter(Role.id == user_role.role_id).first()
#             if role:
#                 roles.append(role.role_name)
#                 if role.role_name == "SuperAdmin":  # Check if the role is 'SuperAdmin'
#                     is_superadmin = True 

#                 # Get permissions for this role
#                 role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
#                 for role_permission in role_permissions:
#                     permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#                     if permission:
#                         permissions.add(permission.permission_name)
        
#         if is_superadmin:
#             continue

#         # Write the user data to the CSV
#         csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_data.csv"})


# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     Authorize.jwt_required()
#     current_user = Authorize.get_jwt_subject()

#     # Retrieve the current user from the database
#     user = db.query(User).filter(User.username == current_user).first()

#     if not user:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

#     # Fetch the roles assigned to the current user
#     user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()

#     roles = [role.role_name for user_role in user_roles for role in [db.query(Role).filter(Role.id == user_role.role_id).first()]]

#     is_superadmin = "SuperAdmin" in roles
#     is_admin = "admin" in roles

#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)
    
#     # Write header to CSV
#     csv_writer.writerow(["user_id", "username", "email", "roles", "permissions"])

#     if is_superadmin :
#         # If the current user is SuperAdmin, include all users except SuperAdmin
#         users = db.query(User).filter(User.username != "SuperAdmin").all()
#     elif is_admin:
#         users = db.query(User).filter(User.username != "SuperAdmin").all()

#         # If the current user is not SuperAdmin or Admin, include only the current user's entry
#     else:
#         users = [user]  # Only add the current user's data

#     # Iterate over the selected users to add them to the CSV
#     for user in users:
#         # Get roles associated with the user
#         user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        
#         roles = []
#         permissions = set()  # Use a set to avoid duplicates
#         for user_role in user_roles:
#             role = db.query(Role).filter(Role.id == user_role.role_id).first()
#             if role:
#                 roles.append(role.role_name)

#                 # Get permissions for this role
#                 role_permissions = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
#                 for role_permission in role_permissions:
#                     permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
#                     if permission:
#                         permissions.add(permission.permission_name)

#         # Write the user data to the CSV
#         csv_writer.writerow([user.id, user.username, user.email, ', '.join(roles), ', '.join(permissions)])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={"Content-Disposition": "attachment; filename=users_data.csv"})

