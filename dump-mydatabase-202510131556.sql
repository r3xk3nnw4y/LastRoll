--
-- PostgreSQL database dump
--

\restrict VgR2dhyqfgngSELAH7BKaCTD4hThdxwued4GlTACEl3cIg5uiDbQDZMTZwaldSC

-- Dumped from database version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)
-- Dumped by pg_dump version 16.10 (Ubuntu 16.10-0ubuntu0.24.04.1)

-- Started on 2025-10-13 15:56:06 CDT

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 3455 (class 1262 OID 16389)
-- Name: mydatabase; Type: DATABASE; Schema: -; Owner: jack
--

CREATE DATABASE mydatabase WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_US.UTF-8';


ALTER DATABASE mydatabase OWNER TO jack;

\unrestrict VgR2dhyqfgngSELAH7BKaCTD4hThdxwued4GlTACEl3cIg5uiDbQDZMTZwaldSC
\connect mydatabase
\restrict VgR2dhyqfgngSELAH7BKaCTD4hThdxwued4GlTACEl3cIg5uiDbQDZMTZwaldSC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
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
-- TOC entry 215 (class 1259 OID 16391)
-- Name: accounts; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.accounts (
    aid integer NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    email character varying NOT NULL,
    role character varying NOT NULL,
    salt character varying
);


ALTER TABLE public.accounts OWNER TO myuser;

--
-- TOC entry 217 (class 1259 OID 16404)
-- Name: listings; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.listings (
    pid integer NOT NULL,
    cost double precision NOT NULL,
    name character varying NOT NULL,
    selleraid integer NOT NULL,
    tags text[]
);


ALTER TABLE public.listings OWNER TO myuser;

--
-- TOC entry 216 (class 1259 OID 16401)
-- Name: orders; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.orders (
    "OID" integer NOT NULL,
    buyerid integer NOT NULL,
    sellerid integer NOT NULL,
    invids bigint[],
    shippingaddr text
);


ALTER TABLE public.orders OWNER TO myuser;

--
-- TOC entry 218 (class 1259 OID 24581)
-- Name: staging; Type: TABLE; Schema: public; Owner: myuser
--

CREATE TABLE public.staging (
    aid integer NOT NULL,
    username character varying NOT NULL,
    password character varying NOT NULL,
    email character varying NOT NULL,
    role character varying NOT NULL,
    salt character varying
);


ALTER TABLE public.staging OWNER TO myuser;

--
-- TOC entry 3446 (class 0 OID 16391)
-- Dependencies: 215
-- Data for Name: accounts; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- TOC entry 3448 (class 0 OID 16404)
-- Dependencies: 217
-- Data for Name: listings; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- TOC entry 3447 (class 0 OID 16401)
-- Dependencies: 216
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- TOC entry 3449 (class 0 OID 24581)
-- Dependencies: 218
-- Data for Name: staging; Type: TABLE DATA; Schema: public; Owner: myuser
--



--
-- TOC entry 3295 (class 2606 OID 16395)
-- Name: accounts accounts_pk; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.accounts
    ADD CONSTRAINT accounts_pk PRIMARY KEY (aid);


--
-- TOC entry 3299 (class 2606 OID 16408)
-- Name: listings listings_pk; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.listings
    ADD CONSTRAINT listings_pk PRIMARY KEY (pid);


--
-- TOC entry 3297 (class 2606 OID 16417)
-- Name: orders orders_pk; Type: CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pk PRIMARY KEY ("OID");


--
-- TOC entry 3302 (class 2606 OID 16411)
-- Name: listings listings_accounts_fk; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.listings
    ADD CONSTRAINT listings_accounts_fk FOREIGN KEY (selleraid) REFERENCES public.accounts(aid) ON DELETE CASCADE;


--
-- TOC entry 3300 (class 2606 OID 32780)
-- Name: orders orders_accounts_fk; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_accounts_fk FOREIGN KEY (buyerid) REFERENCES public.accounts(aid);


--
-- TOC entry 3301 (class 2606 OID 32785)
-- Name: orders orders_accounts_fk_1; Type: FK CONSTRAINT; Schema: public; Owner: myuser
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_accounts_fk_1 FOREIGN KEY (sellerid) REFERENCES public.accounts(aid);


-- Completed on 2025-10-13 15:56:06 CDT

--
-- PostgreSQL database dump complete
--

\unrestrict VgR2dhyqfgngSELAH7BKaCTD4hThdxwued4GlTACEl3cIg5uiDbQDZMTZwaldSC

