"""initial schema

Revision ID: a1b2c3d4e5f6
Revises:
Create Date: 2026-07-14 00:00:00.000000

This migration captures the schema as it already exists in
backend/instance/placement_portal.db. It is meant to be adopted with
`flask db stamp head` on any database that was created before migrations
were introduced (so existing data is left untouched), and used with
`flask db upgrade` to create the schema from scratch on a brand new,
empty database.
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(length=7), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'companies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(length=7), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('company_name', sa.String(length=150), nullable=False),
        sa.Column('hr_contact', sa.String(length=100), nullable=True),
        sa.Column('website', sa.String(length=200), nullable=True),
        sa.Column('approval_status', sa.String(length=11), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_name'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(length=120), nullable=False),
        sa.Column('password', sa.String(length=128), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('role', sa.String(length=7), nullable=False),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('enrollment_number', sa.String(length=20), nullable=False),
        sa.Column('department', sa.String(length=50), nullable=False),
        sa.Column('course', sa.String(length=50), nullable=False),
        sa.Column('skills', sa.String(length=200), nullable=True),
        sa.Column('resume_link', sa.String(length=200), nullable=True),
        sa.Column('is_blacklisted', sa.Boolean(), nullable=False),
        sa.Column('year_of_study', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('enrollment_number'),
        sa.UniqueConstraint('email'),
    )

    op.create_table(
        'placement_drives',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('job_title', sa.String(length=100), nullable=False),
        sa.Column('job_description', sa.Text(), nullable=True),
        sa.Column('eligibility_criteria', sa.Text(), nullable=True),
        sa.Column('drive_start_date', sa.DateTime(), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('salary_range', sa.String(length=50), nullable=True),
        sa.Column('required_skills', sa.String(length=200), nullable=True),
        sa.Column('experience_required', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=9), nullable=False),
        sa.Column('approval_status', sa.String(length=11), nullable=False),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('drive_id', sa.Integer(), nullable=False),
        sa.Column('application_date', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=11), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('resume_link', sa.String(length=200), nullable=False),
        sa.Column('cover_letter', sa.Text(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drive_id'], ['placement_drives.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'student_notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'placements',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('company_id', sa.Integer(), nullable=False),
        sa.Column('drive_id', sa.Integer(), nullable=False),
        sa.Column('application_id', sa.Integer(), nullable=False),
        sa.Column('offer_date', sa.DateTime(), nullable=True),
        sa.Column('join_date', sa.DateTime(), nullable=True),
        sa.Column('package_lpa', sa.String(length=50), nullable=True),
        sa.Column('placed_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['student_id'], ['students.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['company_id'], ['companies.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['drive_id'], ['placement_drives.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('placements')
    op.drop_table('student_notifications')
    op.drop_table('applications')
    op.drop_table('placement_drives')
    op.drop_table('students')
    op.drop_table('companies')
    op.drop_table('admins')
