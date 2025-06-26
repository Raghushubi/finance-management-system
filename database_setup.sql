-- PostgreSQL database 
-- Schema-only with 1 test user for login testing

-- Encoding and setup
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

-- Tables

CREATE TABLE public.asset (
    asset_id integer NOT NULL,
    user_id integer,
    asset_type character varying(50),
    asset_value numeric(10,2),
    purchase_date date
);

CREATE TABLE public.budget (
    budget_id integer NOT NULL,
    user_id integer,
    budget_category character varying(50),
    planned_amount numeric(10,2),
    budget_start_date date,
    budget_end_date date
);

CREATE TABLE public.credit_card (
    credit_card_id integer NOT NULL,
    user_id integer,
    card_number numeric(16,0),
    bank_name character varying(50),
    credit_limit numeric(10,2),
    balance numeric(10,2),
    expiry_date date
);

CREATE TABLE public.investment (
    investment_id integer NOT NULL,
    user_id integer,
    investment_type character varying(50),
    ticker character varying(20),
    units integer,
    purchase_price numeric(10,2),
    current_price numeric(10,2)
);

CREATE TABLE public.liability (
    liability_id integer NOT NULL,
    user_id integer,
    liability_type character varying(50),
    liability_amount numeric(10,2),
    interest_rate numeric(4,2),
    due_date date
);

CREATE TABLE public.phone (
    phone_id integer NOT NULL,
    user_id integer,
    phone_number character varying(10)
);

CREATE TABLE public.transaction_main (
    transaction_id integer NOT NULL,
    user_id integer,
    transaction_amount numeric(10,2),
    transaction_type_id integer,
    transaction_date date
);

CREATE TABLE public.transaction_type (
    transaction_type_id integer NOT NULL,
    transaction_type character varying(50),
    transaction_category character varying(50)
);

CREATE TABLE public.users (
    user_id integer NOT NULL,
    username character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    password character varying(50) NOT NULL
);

-- One test user (valid login for testing)
COPY public.users (user_id, username, email, password) FROM stdin;
1	testuser	test@example.com	test123
\.

-- Primary Keys
ALTER TABLE ONLY public.asset ADD CONSTRAINT asset_pkey PRIMARY KEY (asset_id);
ALTER TABLE ONLY public.budget ADD CONSTRAINT budget_pkey PRIMARY KEY (budget_id);
ALTER TABLE ONLY public.credit_card ADD CONSTRAINT credit_card_pkey PRIMARY KEY (credit_card_id);
ALTER TABLE ONLY public.investment ADD CONSTRAINT investment_pkey PRIMARY KEY (investment_id);
ALTER TABLE ONLY public.liability ADD CONSTRAINT liability_pkey PRIMARY KEY (liability_id);
ALTER TABLE ONLY public.phone ADD CONSTRAINT phone_pkey PRIMARY KEY (phone_id);
ALTER TABLE ONLY public.transaction_main ADD CONSTRAINT transaction_main_pkey PRIMARY KEY (transaction_id);
ALTER TABLE ONLY public.transaction_type ADD CONSTRAINT transaction_type_pkey PRIMARY KEY (transaction_type_id);
ALTER TABLE ONLY public.users ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
ALTER TABLE ONLY public.users ADD CONSTRAINT users_email_key UNIQUE (email);

-- Foreign Keys
ALTER TABLE ONLY public.asset ADD CONSTRAINT asset_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.budget ADD CONSTRAINT budget_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.credit_card ADD CONSTRAINT credit_card_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.investment ADD CONSTRAINT investment_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.liability ADD CONSTRAINT liability_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.phone ADD CONSTRAINT phone_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.transaction_main ADD CONSTRAINT transaction_main_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
ALTER TABLE ONLY public.transaction_main ADD CONSTRAINT transaction_main_transaction_type_id_fkey FOREIGN KEY (transaction_type_id) REFERENCES public.transaction_type(transaction_type_id);

-- Done
