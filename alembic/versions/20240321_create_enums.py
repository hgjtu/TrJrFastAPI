"""create enums

Revision ID: 20240321_create_enums
Revises: 
Create Date: 2024-03-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240321_create_enums'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create PostStatus enum type
    postgresql.ENUM('STATUS_NOT_CHECKED', 'STATUS_VERIFIED', 'STATUS_DENIED', name='poststatus').create(op.get_bind())
    
    # Create Role enum type
    postgresql.ENUM('ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR', name='role').create(op.get_bind())
    
    # Drop default values
    op.execute("ALTER TABLE posts ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    
    # Update existing values in posts table
    op.execute("UPDATE posts SET status = 'STATUS_NOT_CHECKED' WHERE status IS NULL OR status = ''")
    op.execute("UPDATE posts SET status = 'STATUS_NOT_CHECKED' WHERE status NOT IN ('STATUS_NOT_CHECKED', 'STATUS_VERIFIED', 'STATUS_DENIED')")
    
    # Update existing values in users table
    op.execute("UPDATE users SET role = 'ROLE_USER' WHERE role IS NULL OR role = ''")
    op.execute("UPDATE users SET role = 'ROLE_USER' WHERE role NOT IN ('ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR')")
    
    # Update the posts table to use the new poststatus enum type
    op.alter_column('posts', 'status',
                    existing_type=sa.String(),
                    type_=postgresql.ENUM('STATUS_NOT_CHECKED', 'STATUS_VERIFIED', 'STATUS_DENIED', name='poststatus'),
                    postgresql_using='status::poststatus')
    
    # Update the users table to use the new role enum type
    op.alter_column('users', 'role',
                    existing_type=sa.String(),
                    type_=postgresql.ENUM('ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR', name='role'),
                    postgresql_using='role::role')
    
    # Add default values back
    op.execute("ALTER TABLE posts ALTER COLUMN status SET DEFAULT 'STATUS_NOT_CHECKED'::poststatus")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'ROLE_USER'::role")


def downgrade() -> None:
    # Drop default values
    op.execute("ALTER TABLE posts ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    
    # Revert the users table column type
    op.alter_column('users', 'role',
                    existing_type=postgresql.ENUM('ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR', name='role'),
                    type_=sa.String(),
                    postgresql_using='role::text')
    
    # Revert the posts table column type
    op.alter_column('posts', 'status',
                    existing_type=postgresql.ENUM('STATUS_NOT_CHECKED', 'STATUS_VERIFIED', 'STATUS_DENIED', name='poststatus'),
                    type_=sa.String(),
                    postgresql_using='status::text')
    
    # Drop the enum types
    postgresql.ENUM('ROLE_USER', 'ROLE_ADMIN', 'ROLE_MODERATOR', name='role').drop(op.get_bind())
    postgresql.ENUM('STATUS_NOT_CHECKED', 'STATUS_VERIFIED', 'STATUS_DENIED', name='poststatus').drop(op.get_bind())
    
    # Add default values back
    op.execute("ALTER TABLE posts ALTER COLUMN status SET DEFAULT 'STATUS_NOT_CHECKED'")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'ROLE_USER'") 