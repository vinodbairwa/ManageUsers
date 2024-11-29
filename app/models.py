from sqlalchemy import Column, Integer, String, ForeignKey,Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = 'users'  # Corrected

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=True)
    email = Column(String(100), unique=True, nullable=False)
    is_verified = Column(Boolean, default=False) 
    
    roles = relationship("UserRole", back_populates="user",cascade="all, delete-orphan")

class Role(Base):
    __tablename__ = 'roles'  # Corrected

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_name = Column(String(50), unique=True, nullable=False)
    permissions = relationship("RolePermission", back_populates="role",cascade="all, delete-orphan")
    users = relationship("UserRole", back_populates="role",cascade="all, delete-orphan")

class Permission(Base):
    __tablename__ = 'permissions'  # Corrected

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    permission_name = Column(String(50), unique=True, nullable=False)
    roles = relationship("RolePermission", back_populates="permission",cascade="all, delete-orphan")

class RolePermission(Base):
    __tablename__ = 'roles_permissions'  # Corrected

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    role_id = Column(Integer, ForeignKey('roles.id',ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    permission_id = Column(Integer, ForeignKey('permissions.id',ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")

class UserRole(Base):
    __tablename__ = 'user_roles'  # Corrected

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False)

    user = relationship("User", back_populates="roles")
    role = relationship("Role", back_populates="users")


