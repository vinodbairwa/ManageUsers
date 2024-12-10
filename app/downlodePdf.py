# from fastapi import FastAPI
# from .main import *
# from . models import *
# from .jwt import*
# from fastapi.responses import StreamingResponse
# import io
# import csv

# @app.get("/download_users_csv")
# def download_users_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     # Authorize.jwt_required()
    
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





# @app.get("/download_roles_csv")
# def download_roles_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
#     # Authorize.jwt_required()
#     # current_user = Authorize.get_jwt_subject()  # Get the current logged-in user
#     # print(f"current_user",current_user)
#     current_user="dummy"
#     # Fetch the user and their role in a single query
#     user_with_role = (
#         db.query(User, Role)
#         .join(UserRole, User.id == UserRole.user_id)
#         .join(Role, Role.id == UserRole.role_id)
#         .filter(User.username == current_user)
#         .first()
#     )

#     if not user_with_role:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User or role not found")

#     user, role = user_with_role

#     # Check if the user has 'superadmin' role
#     if role.role_name == "SuperAdmin":
#         # Fetch all roles excluding 'superadmin'
#         roles = db.query(Role).filter(Role.role_name != "SuperAdmin").all()
#     else:
#         roles = db.query(Role).filter(Role.role_name != "admin", Role.role_name != "SuperAdmin").all()

#     # Prepare CSV in memory
#     output = io.StringIO()
#     csv_writer = csv.writer(output)

#     # Write the header to CSV
#     csv_writer.writerow(["role_id", "role_name"])

#     # Write the role data to CSV
#     for role in roles:
#         csv_writer.writerow([role.id, role.role_name])

#     # Move the pointer to the beginning of the StringIO buffer
#     output.seek(0)

#     # Return the CSV file as a downloadable file
#     return StreamingResponse(output, media_type="text/csv", headers={
#         "Content-Disposition": "attachment; filename=roles.csv"
#     })




# @app.get("/download_permission_csv")
# def download_permission_csv(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):

#     # Authorize.jwt_required()  # Ensure the request contains a valid JWT

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