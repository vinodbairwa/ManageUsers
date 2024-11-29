from .main import Request,HTMLResponse,Depends,AuthJWT,templates,Session, get_db,app

from .main import *


# @app.get("/", response_class= HTMLResponse)
# def login(request: Request):
#     return templates.TemplateResponse("login.html", {"request": request})

#assign permission
@app.get("/permission", response_class= HTMLResponse)
def permission(request: Request, Authorize: AuthJWT = Depends()):
    return templates.TemplateResponse("add_permission.html", {"request": request})

# create role
@app.get("/roles_create/",response_class= HTMLResponse) 
def roles(request: Request, Authorize: AuthJWT = Depends(),db: Session = Depends(get_db)):
    return templates.TemplateResponse("AddRole.html", {"request": request,})    

# 777285
#assign role to user
@app.get("/user_role_render_page/", response_class=HTMLResponse)
def get_user_role_form(request: Request, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    
    return templates.TemplateResponse("useroleDrop.html", {"request": request,})
    
    
#permission manage
@app.get("/Allpermission/", response_class=HTMLResponse)
def get_permission_role_form(request: Request, db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    return templates.TemplateResponse("per_role.html",{
        "request": request,})

#userDeshbord
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

#change password 
@app.get("/change_pass_render",response_class=HTMLResponse)
def change_render(request:Request, db: Session = Depends(get_db),Authorize: AuthJWT = Depends()):
    return templates.TemplateResponse("change_render.html")


# admin signup html
# @app.get("/signup/", response_class= HTMLResponse)
# def AdminSignup(request: Request):
#     return templates.TemplateResponse("signup.html", {"request": request})

   
# user signup
@app.get("/Usersignup/", response_class= HTMLResponse)
def UserSignup(request: Request):
    return templates.TemplateResponse("UserSignup.html", {"request": request})