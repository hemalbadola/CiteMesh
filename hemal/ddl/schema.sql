-- schema.sql
-- Purpose: PostgreSQL DDL for the Academic Research Paper Repository & Citation Network
-- Usage: psql -d <database> -f schema.sql

SET client_encoding = 'UTF8';
SET standard_conforming_strings = ON;

CREATE EXTENSION IF NOT EXISTS pgcrypto; -- provides gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS citext;   -- case-insensitive text for emails

-- Drop tables in dependency order for repeatable execution
DROP TABLE IF EXISTS reviewer_topic CASCADE;
DROP TABLE IF EXISTS review CASCADE;
DROP TABLE IF EXISTS suggested_citation CASCADE;
DROP TABLE IF EXISTS citation CASCADE;
DROP TABLE IF EXISTS attachment CASCADE;
DROP TABLE IF EXISTS paper_keyword CASCADE;
DROP TABLE IF EXISTS paper_topic CASCADE;
DROP TABLE IF EXISTS paper_author CASCADE;
DROP TABLE IF EXISTS paper_version CASCADE;
DROP TABLE IF EXISTS tag_suggestion CASCADE;
DROP TABLE IF EXISTS notification CASCADE;
DROP TABLE IF EXISTS task CASCADE;
DROP TABLE IF EXISTS audit_log CASCADE;
DROP TABLE IF EXISTS paper CASCADE;
DROP TABLE IF EXISTS author CASCADE;
DROP TABLE IF EXISTS reviewer CASCADE;
DROP TABLE IF EXISTS user_account CASCADE;
DROP TABLE IF EXISTS keyword CASCADE;
DROP TABLE IF EXISTS topic CASCADE;
DROP TABLE IF EXISTS publication_venue CASCADE;
DROP TABLE IF EXISTS institution CASCADE;

-- Core reference entities ----------------------------------------------------

CREATE TABLE institution (
    institution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name           TEXT NOT NULL,
    country        TEXT NOT NULL,
    city           TEXT NOT NULL,
    website_url    TEXT,
    institution_type TEXT NOT NULL CHECK (institution_type IN ('university', 'conference', 'publisher', 'laboratory', 'institute', 'other')),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE institution IS 'Catalog of institutions affiliated with authors, reviewers, and venues.';
COMMENT ON COLUMN institution.name IS 'Official name of the institution; unique with city.';
COMMENT ON COLUMN institution.institution_type IS 'Classification to support reporting and filtering.';
COMMENT ON COLUMN institution.country IS 'Country where the institution operates.';
COMMENT ON COLUMN institution.city IS 'Primary city associated with the institution campus.';
COMMENT ON COLUMN institution.website_url IS 'Public website link for reference in documentation.';
COMMENT ON COLUMN institution.created_at IS 'Timestamp when the institution record was created.';
COMMENT ON COLUMN institution.updated_at IS 'Timestamp of the latest update to the institution record.';

CREATE UNIQUE INDEX ux_institution_name_city ON institution (LOWER(name), LOWER(city));

CREATE TABLE publication_venue (
    venue_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name          TEXT NOT NULL,
    venue_type    TEXT NOT NULL CHECK (venue_type IN ('journal', 'conference', 'workshop', 'preprint', 'technical_report', 'other')),
    publisher     TEXT,
    issn_isbn     TEXT,
    impact_factor NUMERIC(5,2),
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE publication_venue IS 'Publication outlets such as journals or conferences.';
COMMENT ON COLUMN publication_venue.venue_type IS 'Used to classify venue workflows and analytics.';
COMMENT ON COLUMN publication_venue.name IS 'Name of the journal, conference, or venue.';
COMMENT ON COLUMN publication_venue.publisher IS 'Publishing organization or sponsor.';
COMMENT ON COLUMN publication_venue.issn_isbn IS 'Standard identifier for the venue when available.';
COMMENT ON COLUMN publication_venue.impact_factor IS 'Latest recorded impact factor or prestige metric.';
COMMENT ON COLUMN publication_venue.created_at IS 'Timestamp when the venue record was added.';
COMMENT ON COLUMN publication_venue.updated_at IS 'Timestamp of the latest update for the venue.';

CREATE UNIQUE INDEX ux_publication_venue_name ON publication_venue (LOWER(name));
CREATE UNIQUE INDEX ux_publication_venue_issn ON publication_venue (issn_isbn) WHERE issn_isbn IS NOT NULL;

CREATE TABLE topic (
    topic_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name             TEXT NOT NULL,
    description      TEXT,
    parent_topic_id  UUID REFERENCES topic(topic_id) ON DELETE SET NULL,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE topic IS 'Hierarchical representation of research topics using self-references.';
COMMENT ON COLUMN topic.parent_topic_id IS 'Allows nesting topics to support drilling in analytics.';
COMMENT ON COLUMN topic.name IS 'Official display name of the research topic.';
COMMENT ON COLUMN topic.description IS 'Optional explanation or scope for the topic.';
COMMENT ON COLUMN topic.created_at IS 'Timestamp when the topic entry was captured.';

CREATE UNIQUE INDEX ux_topic_name ON topic (LOWER(name));

CREATE TABLE keyword (
    keyword_id  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    term        TEXT NOT NULL,
    description TEXT,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE keyword IS 'Lightweight tagging vocabulary for quick classification.';
COMMENT ON COLUMN keyword.term IS 'Keyword text used for quick tagging.';
COMMENT ON COLUMN keyword.description IS 'Context or definition for the keyword.';
COMMENT ON COLUMN keyword.created_at IS 'Timestamp when the keyword was introduced.';

CREATE UNIQUE INDEX ux_keyword_term ON keyword (LOWER(term));

CREATE TABLE user_account (
    user_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username     CITEXT NOT NULL,
    email        CITEXT NOT NULL,
    role         TEXT NOT NULL CHECK (role IN ('integration_lead', 'data_architect', 'schema_engineer', 'query_specialist', 'reviewer', 'admin', 'other')),
    status       TEXT NOT NULL DEFAULT 'active' CHECK (status IN ('active', 'suspended', 'invited', 'inactive')),
    last_login_at TIMESTAMPTZ,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE user_account IS 'Internal project user accounts used for workflow automation and auditing.';
COMMENT ON COLUMN user_account.username IS 'Display/login name for project tooling.';
COMMENT ON COLUMN user_account.email IS 'Contact email; enforced unique and case-insensitive.';
COMMENT ON COLUMN user_account.role IS 'Role identifier used to scope permissions.';
COMMENT ON COLUMN user_account.status IS 'Lifecycle state of the account (active/suspended/etc.).';
COMMENT ON COLUMN user_account.last_login_at IS 'Last time the user accessed the system.';
COMMENT ON COLUMN user_account.created_at IS 'Timestamp when the user account was created.';
COMMENT ON COLUMN user_account.updated_at IS 'Timestamp when the user account was last updated.';

CREATE UNIQUE INDEX ux_user_account_username ON user_account (username);
CREATE UNIQUE INDEX ux_user_account_email ON user_account (email);

-- People and domain entities -------------------------------------------------

CREATE TABLE author (
    author_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       TEXT NOT NULL,
    email           CITEXT,
    affiliation_id  UUID REFERENCES institution(institution_id) ON DELETE SET NULL,
    orcid           TEXT,
    h_index         INTEGER CHECK (h_index IS NULL OR h_index >= 0),
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE author IS 'Authors contributing research papers to the repository.';
COMMENT ON COLUMN author.orcid IS 'Optional ORCID identifier (####-####-####-####).';
COMMENT ON COLUMN author.full_name IS 'Author full name for display and search.';
COMMENT ON COLUMN author.email IS 'Optional contact email for the author.';
COMMENT ON COLUMN author.affiliation_id IS 'Institution affiliation for reporting and filtering.';
COMMENT ON COLUMN author.h_index IS 'Bibliometric h-index metric when available.';
COMMENT ON COLUMN author.created_at IS 'Timestamp when the author record was added.';
COMMENT ON COLUMN author.updated_at IS 'Timestamp for the latest author record update.';

CREATE UNIQUE INDEX ux_author_email ON author (email) WHERE email IS NOT NULL;
CREATE UNIQUE INDEX ux_author_orcid ON author (orcid) WHERE orcid IS NOT NULL;
CREATE INDEX idx_author_full_name ON author (LOWER(full_name));

CREATE TABLE reviewer (
    reviewer_id     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name       TEXT NOT NULL,
    email           CITEXT,
    institution_id  UUID REFERENCES institution(institution_id) ON DELETE SET NULL,
    expertise_notes TEXT,
    active_since    DATE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE reviewer IS 'Reviewers providing feedback on submitted papers.';
COMMENT ON COLUMN reviewer.full_name IS 'Reviewer full name.';
COMMENT ON COLUMN reviewer.email IS 'Contact email for the reviewer.';
COMMENT ON COLUMN reviewer.institution_id IS 'Affiliated institution for reviewer expertise.';
COMMENT ON COLUMN reviewer.expertise_notes IS 'Free-form notes describing reviewer strengths.';
COMMENT ON COLUMN reviewer.active_since IS 'Date the reviewer started collaborating.';
COMMENT ON COLUMN reviewer.created_at IS 'Timestamp when the reviewer was registered.';

CREATE UNIQUE INDEX ux_reviewer_email ON reviewer (email) WHERE email IS NOT NULL;
CREATE INDEX idx_reviewer_full_name ON reviewer (LOWER(full_name));

CREATE TABLE paper (
    paper_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title               TEXT NOT NULL,
    abstract            TEXT,
    publication_year    SMALLINT NOT NULL CHECK (publication_year BETWEEN 1900 AND 2100),
    doi                 TEXT,
    submission_status   TEXT NOT NULL DEFAULT 'draft' CHECK (submission_status IN ('draft', 'under_review', 'accepted', 'rejected', 'published')),
    institution_id      UUID REFERENCES institution(institution_id) ON DELETE SET NULL,
    venue_id            UUID REFERENCES publication_venue(venue_id) ON DELETE SET NULL,
    created_by_user_id  UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE paper IS 'Core research paper records with linkage to authors, venues, and institutions.';
COMMENT ON COLUMN paper.submission_status IS 'Tracks lifecycle state for workflow management.';
COMMENT ON COLUMN paper.title IS 'Paper title; search indexed.';
COMMENT ON COLUMN paper.abstract IS 'Abstract text summarizing the research.';
COMMENT ON COLUMN paper.publication_year IS 'Publication year for reporting and filtering.';
COMMENT ON COLUMN paper.doi IS 'Digital Object Identifier when available.';
COMMENT ON COLUMN paper.institution_id IS 'Primary institution responsible for the paper.';
COMMENT ON COLUMN paper.venue_id IS 'Publication venue associated with the paper.';
COMMENT ON COLUMN paper.created_by_user_id IS 'User account that registered the paper.';
COMMENT ON COLUMN paper.created_at IS 'Timestamp when the paper record was created.';
COMMENT ON COLUMN paper.updated_at IS 'Timestamp for the latest update to the paper record.';

CREATE UNIQUE INDEX ux_paper_doi ON paper (doi) WHERE doi IS NOT NULL;
CREATE INDEX idx_paper_title ON paper (LOWER(title));
CREATE INDEX idx_paper_publication_year ON paper (publication_year);

CREATE TABLE paper_version (
    version_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id            UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    version_number      INTEGER NOT NULL CHECK (version_number >= 1),
    submitted_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    submitted_by_author_id UUID REFERENCES author(author_id) ON DELETE SET NULL,
    file_uri            TEXT NOT NULL,
    checksum            TEXT,
    change_log          TEXT
);
COMMENT ON TABLE paper_version IS 'Version history for papers to support revision tracking.';
COMMENT ON COLUMN paper_version.paper_id IS 'Parent paper for the version entry.';
COMMENT ON COLUMN paper_version.version_number IS 'Sequential version identifier starting at 1.';
COMMENT ON COLUMN paper_version.submitted_at IS 'Submission time for this version.';
COMMENT ON COLUMN paper_version.submitted_by_author_id IS 'Author who submitted the revision.';
COMMENT ON COLUMN paper_version.file_uri IS 'Location of the stored manuscript file.';
COMMENT ON COLUMN paper_version.checksum IS 'Hash value to detect file tampering.';
COMMENT ON COLUMN paper_version.change_log IS 'Narrative of what changed in this revision.';

CREATE UNIQUE INDEX ux_paper_version_unique ON paper_version (paper_id, version_number);

CREATE TABLE paper_author (
    paper_id        UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    author_id       UUID NOT NULL REFERENCES author(author_id) ON DELETE CASCADE,
    author_order    INTEGER NOT NULL CHECK (author_order >= 1),
    contribution_type TEXT NOT NULL DEFAULT 'primary' CHECK (contribution_type IN ('primary', 'co_author', 'editor', 'advisor')),
    added_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (paper_id, author_id)
);
COMMENT ON TABLE paper_author IS 'Junction table linking papers to authors with ordering and contribution details.';
COMMENT ON COLUMN paper_author.paper_id IS 'Identifier of the associated paper.';
COMMENT ON COLUMN paper_author.author_id IS 'Identifier of the linked author.';
COMMENT ON COLUMN paper_author.author_order IS 'Position of the author for display/citation formatting.';
COMMENT ON COLUMN paper_author.contribution_type IS 'Role played by the author on the paper.';
COMMENT ON COLUMN paper_author.added_at IS 'Timestamp when the author-paper link was created.';

CREATE UNIQUE INDEX ux_paper_author_order ON paper_author (paper_id, author_order);

CREATE TABLE paper_topic (
    paper_id       UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    topic_id       UUID NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE,
    relevance_score NUMERIC(5,4) CHECK (relevance_score IS NULL OR (relevance_score >= 0 AND relevance_score <= 1)),
    tagged_by_user_id UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    tagged_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (paper_id, topic_id)
);
COMMENT ON TABLE paper_topic IS 'Associates papers with curated topics, optionally weighted by relevance.';
COMMENT ON COLUMN paper_topic.paper_id IS 'Paper being tagged with the topic.';
COMMENT ON COLUMN paper_topic.topic_id IS 'Topic applied to the paper.';
COMMENT ON COLUMN paper_topic.relevance_score IS 'Optional numeric weight for topic relevance.';
COMMENT ON COLUMN paper_topic.tagged_by_user_id IS 'User who attached the topic to the paper.';
COMMENT ON COLUMN paper_topic.tagged_at IS 'Timestamp when the topic link was registered.';

CREATE TABLE paper_keyword (
    paper_id    UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    keyword_id  UUID NOT NULL REFERENCES keyword(keyword_id) ON DELETE CASCADE,
    tagged_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (paper_id, keyword_id)
);
COMMENT ON TABLE paper_keyword IS 'Optional keyword tagging to complement topic taxonomy.';
COMMENT ON COLUMN paper_keyword.paper_id IS 'Paper associated with the keyword.';
COMMENT ON COLUMN paper_keyword.keyword_id IS 'Keyword attached to the paper.';
COMMENT ON COLUMN paper_keyword.tagged_at IS 'Timestamp when the keyword was applied to the paper.';

CREATE TABLE attachment (
    attachment_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id        UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    attachment_type TEXT NOT NULL CHECK (attachment_type IN ('dataset', 'supplement', 'code', 'presentation', 'other')),
    file_uri        TEXT NOT NULL,
    uploaded_by_user_id UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    uploaded_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    checksum        TEXT
);
COMMENT ON TABLE attachment IS 'Supplementary files linked to papers (datasets, code, etc.).';
COMMENT ON COLUMN attachment.paper_id IS 'Paper that the attachment belongs to.';
COMMENT ON COLUMN attachment.attachment_type IS 'Category of supplemental material.';
COMMENT ON COLUMN attachment.file_uri IS 'Storage location for the file asset.';
COMMENT ON COLUMN attachment.uploaded_by_user_id IS 'User who uploaded the attachment.';
COMMENT ON COLUMN attachment.uploaded_at IS 'Timestamp when the attachment was stored.';
COMMENT ON COLUMN attachment.checksum IS 'Optional integrity hash of the attachment content.';

CREATE INDEX idx_attachment_paper_id ON attachment (paper_id);

CREATE TABLE citation (
    citation_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    citing_paper_id   UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    cited_paper_id    UUID NOT NULL REFERENCES paper(paper_id) ON DELETE RESTRICT,
    citation_type     TEXT NOT NULL DEFAULT 'reference' CHECK (citation_type IN ('reference', 'influence', 'self', 'background')),
    citation_context  TEXT,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE citation IS 'Captures directed relationships between papers for the citation graph.';
COMMENT ON COLUMN citation.citing_paper_id IS 'Paper that references another work.';
COMMENT ON COLUMN citation.cited_paper_id IS 'Paper being referenced in the citation.';
COMMENT ON COLUMN citation.citation_type IS 'Classification of the citation relationship.';
COMMENT ON COLUMN citation.citation_context IS 'Snippet or description of how the citation is used.';
COMMENT ON COLUMN citation.created_at IS 'Timestamp for when the citation was recorded.';

CREATE UNIQUE INDEX ux_citation_pair_type ON citation (citing_paper_id, cited_paper_id, citation_type);
CREATE INDEX idx_citation_citing ON citation (citing_paper_id);
CREATE INDEX idx_citation_cited ON citation (cited_paper_id);

CREATE TABLE suggested_citation (
    suggestion_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    source_paper_id          UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    suggested_cited_paper_id UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    confidence_score         NUMERIC(5,4) NOT NULL CHECK (confidence_score >= 0 AND confidence_score <= 1),
    status                   TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'accepted', 'dismissed')),
    rationale                TEXT,
    suggested_by_user_id     UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    resolved_at              TIMESTAMPTZ
);
COMMENT ON TABLE suggested_citation IS 'System or user generated recommendations for missing citations.';
COMMENT ON COLUMN suggested_citation.source_paper_id IS 'Paper that should add the suggested citation.';
COMMENT ON COLUMN suggested_citation.suggested_cited_paper_id IS 'Paper recommended as a missing citation.';
COMMENT ON COLUMN suggested_citation.confidence_score IS 'Probability or confidence metric for the suggestion.';
COMMENT ON COLUMN suggested_citation.status IS 'Workflow state of the suggestion (pending/accepted/dismissed).';
COMMENT ON COLUMN suggested_citation.rationale IS 'Explanation supporting the recommendation.';
COMMENT ON COLUMN suggested_citation.suggested_by_user_id IS 'User or system account that proposed the suggestion.';
COMMENT ON COLUMN suggested_citation.created_at IS 'Timestamp when the suggestion was created.';
COMMENT ON COLUMN suggested_citation.resolved_at IS 'Timestamp when the suggestion was resolved.';

CREATE UNIQUE INDEX ux_suggested_citation_pair ON suggested_citation (source_paper_id, suggested_cited_paper_id);
CREATE INDEX idx_suggested_citation_status ON suggested_citation (status);

CREATE TABLE review (
    review_id      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id       UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    reviewer_id    UUID NOT NULL REFERENCES reviewer(reviewer_id) ON DELETE CASCADE,
    review_round   SMALLINT NOT NULL DEFAULT 1 CHECK (review_round >= 1),
    score          NUMERIC(3,1) CHECK (score IS NULL OR (score >= 0 AND score <= 5)),
    recommendation TEXT CHECK (recommendation IS NULL OR recommendation IN ('accept', 'minor_revision', 'major_revision', 'reject')),
    comments       TEXT,
    submitted_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE review IS 'Stores structured reviewer feedback for submitted papers.';
COMMENT ON COLUMN review.paper_id IS 'Paper undergoing review.';
COMMENT ON COLUMN review.reviewer_id IS 'Reviewer providing the feedback.';
COMMENT ON COLUMN review.review_round IS 'Iteration counter for resubmissions.';
COMMENT ON COLUMN review.score IS 'Quantitative rating supplied by the reviewer.';
COMMENT ON COLUMN review.recommendation IS 'Reviewer decision recommendation.';
COMMENT ON COLUMN review.comments IS 'Qualitative feedback captured during review.';
COMMENT ON COLUMN review.submitted_at IS 'Timestamp when the review was submitted.';

CREATE UNIQUE INDEX ux_review_assignment ON review (paper_id, reviewer_id, review_round);

CREATE TABLE reviewer_topic (
    reviewer_id   UUID NOT NULL REFERENCES reviewer(reviewer_id) ON DELETE CASCADE,
    topic_id      UUID NOT NULL REFERENCES topic(topic_id) ON DELETE CASCADE,
    expertise_level TEXT CHECK (expertise_level IS NULL OR expertise_level IN ('high', 'medium', 'low')),
    PRIMARY KEY (reviewer_id, topic_id)
);
COMMENT ON TABLE reviewer_topic IS 'Maps reviewer expertise to topics for assignment algorithms.';
COMMENT ON COLUMN reviewer_topic.reviewer_id IS 'Reviewer linked to the expertise entry.';
COMMENT ON COLUMN reviewer_topic.topic_id IS 'Topic describing the reviewer expertise.';
COMMENT ON COLUMN reviewer_topic.expertise_level IS 'Self-assessed or curated reviewer expertise level.';

CREATE TABLE notification (
    notification_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_user_id  UUID NOT NULL REFERENCES user_account(user_id) ON DELETE CASCADE,
    message            TEXT NOT NULL,
    notification_type  TEXT NOT NULL CHECK (notification_type IN ('workflow', 'alert', 'reminder', 'information')),
    seen_at            TIMESTAMPTZ,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE notification IS 'Internal notifications delivered to project users.';
COMMENT ON COLUMN notification.recipient_user_id IS 'User that should receive the notification.';
COMMENT ON COLUMN notification.message IS 'Notification body sent to the user.';
COMMENT ON COLUMN notification.notification_type IS 'Category describing why the notification was issued.';
COMMENT ON COLUMN notification.seen_at IS 'Timestamp when the user acknowledged the notification.';
COMMENT ON COLUMN notification.created_at IS 'Timestamp when the notification was generated.';

CREATE INDEX idx_notification_recipient ON notification (recipient_user_id, seen_at);

CREATE TABLE tag_suggestion (
    suggestion_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    paper_id        UUID NOT NULL REFERENCES paper(paper_id) ON DELETE CASCADE,
    suggested_term  TEXT NOT NULL,
    confidence_score NUMERIC(5,4) CHECK (confidence_score IS NULL OR (confidence_score >= 0 AND confidence_score <= 1)),
    suggested_by_user_id UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE tag_suggestion IS 'Stores machine or user generated metadata enrichment suggestions.';
COMMENT ON COLUMN tag_suggestion.paper_id IS 'Paper associated with the suggested tag.';
COMMENT ON COLUMN tag_suggestion.suggested_term IS 'Keyword/term being suggested.';
COMMENT ON COLUMN tag_suggestion.confidence_score IS 'Confidence indicator for the suggestion.';
COMMENT ON COLUMN tag_suggestion.suggested_by_user_id IS 'User who proposed the tag (null if automated).';
COMMENT ON COLUMN tag_suggestion.created_at IS 'Timestamp when the tag suggestion was captured.';

CREATE INDEX idx_tag_suggestion_paper ON tag_suggestion (paper_id);

CREATE TABLE task (
    task_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title            TEXT NOT NULL,
    description      TEXT,
    assigned_to_user_id UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    due_date         DATE,
    status           TEXT NOT NULL DEFAULT 'todo' CHECK (status IN ('todo', 'in_progress', 'blocked', 'done')),
    related_entity   TEXT,
    related_id       UUID,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE task IS 'Operational tasks for coordinating project activities.';
COMMENT ON COLUMN task.title IS 'Short description of the task.';
COMMENT ON COLUMN task.description IS 'Detailed notes for the task execution.';
COMMENT ON COLUMN task.assigned_to_user_id IS 'User responsible for completing the task.';
COMMENT ON COLUMN task.due_date IS 'Deadline for task completion.';
COMMENT ON COLUMN task.status IS 'Kanban-style state flag for the task.';
COMMENT ON COLUMN task.related_entity IS 'Entity type the task concerns (paper, citation, etc.).';
COMMENT ON COLUMN task.related_id IS 'Identifier of the related entity.';
COMMENT ON COLUMN task.created_at IS 'Timestamp when the task was created.';
COMMENT ON COLUMN task.updated_at IS 'Timestamp tracking the latest task update.';

CREATE INDEX idx_task_status_due_date ON task (status, due_date);

CREATE TABLE audit_log (
    audit_id        BIGSERIAL PRIMARY KEY,
    entity_name     TEXT NOT NULL,
    entity_id       UUID,
    action          TEXT NOT NULL,
    action_by_user_id UUID REFERENCES user_account(user_id) ON DELETE SET NULL,
    action_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    change_summary  TEXT
);
COMMENT ON TABLE audit_log IS 'Append-only log capturing changes to repository entities for traceability.';
COMMENT ON COLUMN audit_log.entity_name IS 'Name of the entity being tracked (paper, author, etc.).';
COMMENT ON COLUMN audit_log.entity_id IS 'Identifier of the entity impacted by the action.';
COMMENT ON COLUMN audit_log.action IS 'Operation performed (INSERT/UPDATE/DELETE/etc.).';
COMMENT ON COLUMN audit_log.action_by_user_id IS 'User who triggered the change.';
COMMENT ON COLUMN audit_log.action_at IS 'Timestamp when the action occurred.';
COMMENT ON COLUMN audit_log.change_summary IS 'Narrative summary of the change for quick review.';

CREATE INDEX idx_audit_log_entity ON audit_log (entity_name, entity_id);
CREATE INDEX idx_audit_log_action_at ON audit_log (action_at DESC);

-- End of schema --------------------------------------------------------------
