from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock


class ConversationStateStore:
    """
    Simple in-memory conversation store.

    Stage 17.9:
    - remembers active workflow
    - remembers collected fields
    - remembers recent messages

    Production upgrade later:
    SQL / Redis / persistent conversation store.
    """

    def __init__(self):
        self._states = {}
        self._lock = Lock()


    def _new_state(
        self,
        session_id: str
    ):
        now = datetime.now(
            timezone.utc
        ).isoformat()

        return {
            "session_id":
                session_id,

            "active_intent":
                None,

            "slots":
                {},

            "history":
                [],

            "created_at":
                now,

            "updated_at":
                now,
        }


    def get(
        self,
        session_id: str
    ):
        with self._lock:

            if session_id not in self._states:
                self._states[
                    session_id
                ] = self._new_state(
                    session_id
                )

            return deepcopy(
                self._states[
                    session_id
                ]
            )


    def save(
        self,
        state: dict
    ):
        state = deepcopy(
            state
        )

        state[
            "updated_at"
        ] = datetime.now(
            timezone.utc
        ).isoformat()

        with self._lock:
            self._states[
                state[
                    "session_id"
                ]
            ] = state


    def clear(
        self,
        session_id: str
    ):
        with self._lock:
            return (
                self._states.pop(
                    session_id,
                    None
                )
                is not None
            )


conversation_store = (
    ConversationStateStore()
)
