--
-- PostgreSQL database dump
--

\restrict GNFsWoVKnM0FfVz8Nzsf1UvwTLz16AnfZG4IBHdWtOv7dOPc653ftRmm6EUPQUC

-- Dumped from database version 18.4
-- Dumped by pg_dump version 18.4

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    category_id bigint NOT NULL,
    category_name character varying(100) NOT NULL,
    description text,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.categories ALTER COLUMN category_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.categories_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: category_rules; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.category_rules (
    rule_id bigint NOT NULL,
    bank_parent_category character varying(100) NOT NULL,
    category_id bigint NOT NULL,
    cash_flow_class character varying(30) NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: category_rules_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.category_rules ALTER COLUMN rule_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.category_rules_rule_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: statements; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.statements (
    statement_id bigint NOT NULL,
    bank_name character varying(100) NOT NULL,
    account_label character varying(100),
    period_start date NOT NULL,
    period_end date NOT NULL,
    imported_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_statement_dates CHECK ((period_end >= period_start))
);


--
-- Name: statements_statement_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.statements ALTER COLUMN statement_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.statements_statement_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: transactions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.transactions (
    transaction_id bigint NOT NULL,
    statement_id bigint NOT NULL,
    category_id bigint,
    source_row_nr integer NOT NULL,
    posting_date timestamp without time zone,
    transaction_date timestamp without time zone,
    description text,
    original_description text,
    parent_category character varying(100),
    bank_category character varying(100),
    transaction_type character varying(30),
    cash_flow_class character varying(30),
    money_in numeric(15,2),
    money_out numeric(15,2),
    fee numeric(15,2),
    balance numeric(15,2),
    transaction_amount numeric(15,2),
    cash_flow numeric(15,2),
    posting_delay_days integer,
    review_required boolean DEFAULT false NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: transactions_transaction_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.transactions ALTER COLUMN transaction_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.transactions_transaction_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: categories categories_category_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_category_name_key UNIQUE (category_name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: category_rules category_rules_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_rules
    ADD CONSTRAINT category_rules_pkey PRIMARY KEY (rule_id);


--
-- Name: statements statements_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.statements
    ADD CONSTRAINT statements_pkey PRIMARY KEY (statement_id);


--
-- Name: transactions transactions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_pkey PRIMARY KEY (transaction_id);


--
-- Name: category_rules uq_bank_parent_category; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_rules
    ADD CONSTRAINT uq_bank_parent_category UNIQUE (bank_parent_category);


--
-- Name: transactions uq_statement_source_row; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT uq_statement_source_row UNIQUE (statement_id, source_row_nr);


--
-- Name: category_rules category_rules_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.category_rules
    ADD CONSTRAINT category_rules_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- Name: transactions transactions_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- Name: transactions transactions_statement_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.transactions
    ADD CONSTRAINT transactions_statement_id_fkey FOREIGN KEY (statement_id) REFERENCES public.statements(statement_id);


--
-- PostgreSQL database dump complete
--

\unrestrict GNFsWoVKnM0FfVz8Nzsf1UvwTLz16AnfZG4IBHdWtOv7dOPc653ftRmm6EUPQUC
