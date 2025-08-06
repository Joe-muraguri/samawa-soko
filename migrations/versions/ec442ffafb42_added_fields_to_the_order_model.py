"""Added fields to the order  model

Revision ID: ec442ffafb42
Revises: a9173790ab09
Create Date: 2025-08-06 13:09:41.880435

"""
from alembic import op
import sqlalchemy as sa


from sqlalchemy.dialects import postgresql
import uuid


# revision identifiers, used by Alembic.
revision = 'ec442ffafb42'
down_revision = 'a9173790ab09'
branch_labels = None
depends_on = None


def upgrade():
    # Just add UUID column without changing primary key
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('uuid', postgresql.UUID(as_uuid=True),
                          nullable=False, 
                          server_default=sa.text('gen_random_uuid()')))
        batch_op.create_unique_constraint('order_uuid_key', ['uuid'])

def downgrade():
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.drop_constraint('order_uuid_key', type_='unique')
        batch_op.drop_column('uuid')