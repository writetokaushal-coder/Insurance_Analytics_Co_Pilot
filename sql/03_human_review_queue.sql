USE InsuranceAnalyticsDB;
GO


IF NOT EXISTS
(
    SELECT 1
    FROM sys.schemas
    WHERE name = 'analytics'
)
BEGIN
    EXEC(
        'CREATE SCHEMA analytics'
    );
END;
GO


IF OBJECT_ID(
    'analytics.human_review_queue',
    'U'
) IS NULL
BEGIN

    CREATE TABLE
        analytics.human_review_queue
    (
        REVIEW_ID
            INT IDENTITY(1,1)
            PRIMARY KEY,

        DOMAIN
            VARCHAR(50)
            NOT NULL,

        ENTITY_ID
            VARCHAR(100)
            NOT NULL,

        REQUESTED_ACTION
            VARCHAR(100)
            NOT NULL,

        AI_RECOMMENDATION
            NVARCHAR(500)
            NULL,

        AI_SCORE
            DECIMAL(10,6)
            NULL,

        REASON
            NVARCHAR(1000)
            NULL,

        STATUS
            VARCHAR(30)
            NOT NULL
            DEFAULT 'PENDING_REVIEW',

        CREATED_AT
            DATETIME2
            NOT NULL
            DEFAULT SYSUTCDATETIME(),

        REVIEWED_AT
            DATETIME2
            NULL,

        REVIEWED_BY
            NVARCHAR(200)
            NULL,

        HUMAN_DECISION
            VARCHAR(30)
            NULL,

        HUMAN_COMMENTS
            NVARCHAR(2000)
            NULL,

        CONSTRAINT CK_HUMAN_REVIEW_STATUS
        CHECK
        (
            STATUS IN
            (
                'PENDING_REVIEW',
                'COMPLETED'
            )
        ),

        CONSTRAINT CK_HUMAN_DECISION
        CHECK
        (
            HUMAN_DECISION IS NULL
            OR
            HUMAN_DECISION IN
            (
                'APPROVED',
                'MODIFIED',
                'REJECTED'
            )
        )
    );

END;
GO


IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name =
        'IX_human_review_pending'
      AND object_id =
        OBJECT_ID(
            'analytics.human_review_queue'
        )
)
BEGIN

    CREATE INDEX
        IX_human_review_pending

    ON
        analytics.human_review_queue
        (
            STATUS,
            CREATED_AT
        );

END;
GO


SELECT TOP 10
    *
FROM analytics.human_review_queue
ORDER BY REVIEW_ID DESC;
GO
