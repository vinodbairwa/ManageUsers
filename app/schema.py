from fastapi import Form
from pydantic import BaseModel, EmailStr
from typing import List, Optional,Dict


# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str
    
#     class Config:
#         orm_mode = True

# class UserLogin(BaseModel):
#     username: str = Form(...)
#     password: str = Form(...)




# class UserRoleCreate(BaseModel):
#     username: str
#     role_names: str
    
    
class PermissionRoleCreate(BaseModel):
    role_name: str
    permission_names: List[str]
   

    
# class EmailRequest(BaseModel):
#     to_email: str
#     subject: str
#     body: str
 
# class ChangePasswordRequest(BaseModel):
#     # email: str
#     old_password: str
#     new_password: str
    
# # Fogot Password
# class EmailRequest(BaseModel):
#     email: EmailStr


# #otp verification
# class OTPVerifyRequest(BaseModel):
#     verification_code: str
    
# #reset password
# class ResetPasswordRequest(BaseModel):
#     email: EmailStr
#     new_password: str
#     confirm_password: str
    
    
    
    
# # class UserCreate:
# #     id: int
# #     username: str
# #     password: str


# # class UserRoleCreate:
# #     user_id: int
# #     role_id: int


# # class Role:
# #     id: int
# #     role_name: str    