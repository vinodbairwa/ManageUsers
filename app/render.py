from pathlib import Path
from fastapi import HTTPException
from fastapi.responses import FileResponse
from .main import Request,HTMLResponse,Depends,AuthJWT,templates,Session, get_db,app
from .main import *




@app.get("/Render/{page_name}", response_class=HTMLResponse)
def Render__page_Html(request: Request, page_name: str,Authorize: AuthJWT = Depends()):
    try:
        Authorize.jwt_required()  # Validate JWT token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Unauthorized")



@app.get("/Udeshbord", response_class=HTMLResponse)
async def Super(request: Request):
    return templates.TemplateResponse("UserDeshbord.html", {"request": request})

#admin deshbord
@app.get("/admin", response_class=HTMLResponse)
async def Super(request: Request):
    return templates.TemplateResponse("AdminDeshbord.html", {"request": request})

@app.get("/SuperAdminDeshbord", response_class=HTMLResponse)
def Superadmin_deshbord(request: Request,db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    return templates.TemplateResponse("SuperAdmin.html", {"request": request})


@app.get("/Usersignup/", response_class= HTMLResponse)
def UserSignup(request: Request):
    return templates.TemplateResponse("UserSignup.html", {"request": request})



# @app.get("/SuperAdmin/update/{user_id}", response_class=HTMLResponse)
# def UpdateSuperAdmin(
#     user_id: int,  # Adding user_id as a positional argument
#     request: Request,
#     db: Session = Depends(get_db),
#     Authorize: AuthJWT = Depends(),
# ):
#     try:
#         Authorize.jwt_required()  # Validate JWT token
#         static_file_path = Path(__file__).parent.parent / "static" / "update.html"
#         return FileResponse(static_file_path)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")
    

   


# @app.get("/permission", response_class=HTMLResponse)
# def permission(request: Request, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()  # Validate JWT token
#         return FileResponse("/static/add_permission.html")
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")
    


# @app.get("/role_create_render/", response_class=HTMLResponse)
# def roles(request: Request, Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required()  # Validate JWT token
#         static_file_path = Path(__file__).parent.parent / "static" / "AddRole.html"
#         return FileResponse(static_file_path)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")




# #assign role to user
# @app.get("/user_role_render_page/", response_class=HTMLResponse)
# def get_user_role_form(request: Request, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required() 
#         static_file_path = Path(__file__).parent.parent / "static" / "useroleDrop.html"
#         return FileResponse(static_file_path)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")



#permission manage
# @app.get("/Allpermission/", response_class=HTMLResponse)
# def get_permission_role_form(request: Request, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required() 
#         static_file_path = Path(__file__).parent.parent / "static" / "per_role.html"
#         return FileResponse(static_file_path)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")
    

# update SuperAdmin , Admin And All the Users  update itself deshbord
# @app.get("/UserUpdateItSelf/",response_class=HTMLResponse)
# async def updateItself_load(request: Request,  db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     try:
#         Authorize.jwt_required() 
#         static_file_path = Path(__file__).parent.parent / "static" / "ItselfUpdate.html"
#         return FileResponse(static_file_path)
#     except Exception as e:
#         raise HTTPException(status_code=401, detail="Unauthorized")
  



#change password 
# @app.get("/change_pass",response_class=HTMLResponse)
# def change_pass(request:Request):
#     return templates.TemplateResponse("changePassword.html", {"request": request})









#userDeshbord


# admin signup html
# @app.get("/signup/", response_class= HTMLResponse)
# def AdminSignup(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})

   
# user signup
