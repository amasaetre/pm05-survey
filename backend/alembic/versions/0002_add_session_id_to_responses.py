from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0002'
down_revision: Union[str, None] = '0001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('responses', sa.Column('session_id', sa.String(), nullable=True))
    op.create_index('ix_responses_session_id', 'responses', ['session_id'])


def downgrade() -> None:
    op.drop_index('ix_responses_session_id', table_name='responses')
    op.drop_column('responses', 'session_id')

