--
-- PostgreSQL database dump
--

\restrict 6QBk2pQlCFPo9LTGs44HtZAwwq1zmBRmc6a7gyOzVXzff7mYPzFcJF9f3d6s08Z

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

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

--
-- Name: recipes; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA recipes;


--
-- Name: SCHEMA recipes; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA recipes IS 'standard public schema';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alt_ingredients; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.alt_ingredients (
    ingredient_id integer NOT NULL,
    alt_ingredient character varying NOT NULL
);


--
-- Name: ingredients; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.ingredients (
    ingredient_id integer NOT NULL,
    ingredient character varying
);


--
-- Name: measurements; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.measurements (
    measurement_id integer NOT NULL,
    measurement character varying
);


--
-- Name: recipe_relationships; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.recipe_relationships (
    ingredient_id integer NOT NULL,
    recipe_id character varying NOT NULL,
    measurement_amount real,
    measurement_id integer
);


--
-- Name: recipes; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.recipes (
    recipe_id character varying NOT NULL,
    name character varying,
    source character varying,
    youtube character varying,
    category character varying
);


--
-- Name: recipes_old; Type: TABLE; Schema: recipes; Owner: -
--

CREATE TABLE recipes.recipes_old (
    recipe_id character varying NOT NULL,
    name character varying NOT NULL,
    category character varying,
    ethnicity character varying,
    tags character varying[],
    ingredients character varying[] NOT NULL,
    measurements character varying[],
    source character varying,
    youtube character varying,
    normalized_ingredients character varying[]
);


--
-- Name: alt_ingredients alt_ingr_relationships_pkey; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.alt_ingredients
    ADD CONSTRAINT alt_ingr_relationships_pkey PRIMARY KEY (alt_ingredient, ingredient_id);


--
-- Name: ingredients ingredients_pkey; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.ingredients
    ADD CONSTRAINT ingredients_pkey PRIMARY KEY (ingredient_id);


--
-- Name: measurements measurements_pkey; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.measurements
    ADD CONSTRAINT measurements_pkey PRIMARY KEY (measurement_id);


--
-- Name: recipe_relationships recipe_relationships_pkey; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipe_relationships
    ADD CONSTRAINT recipe_relationships_pkey PRIMARY KEY (ingredient_id, recipe_id);


--
-- Name: recipes_old recipes_pkey; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipes_old
    ADD CONSTRAINT recipes_pkey PRIMARY KEY (recipe_id);


--
-- Name: recipes recipes_pkey1; Type: CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipes
    ADD CONSTRAINT recipes_pkey1 PRIMARY KEY (recipe_id);


--
-- Name: recipe_relationships ingredient_id_fk; Type: FK CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipe_relationships
    ADD CONSTRAINT ingredient_id_fk FOREIGN KEY (ingredient_id) REFERENCES recipes.ingredients(ingredient_id);


--
-- Name: alt_ingredients ingredient_id_fk; Type: FK CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.alt_ingredients
    ADD CONSTRAINT ingredient_id_fk FOREIGN KEY (ingredient_id) REFERENCES recipes.ingredients(ingredient_id) NOT VALID;


--
-- Name: recipe_relationships measurement_id_fk; Type: FK CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipe_relationships
    ADD CONSTRAINT measurement_id_fk FOREIGN KEY (measurement_id) REFERENCES recipes.measurements(measurement_id) NOT VALID;


--
-- Name: recipe_relationships recipe_id_fk; Type: FK CONSTRAINT; Schema: recipes; Owner: -
--

ALTER TABLE ONLY recipes.recipe_relationships
    ADD CONSTRAINT recipe_id_fk FOREIGN KEY (recipe_id) REFERENCES recipes.recipes(recipe_id);


--
-- PostgreSQL database dump complete
--

\unrestrict 6QBk2pQlCFPo9LTGs44HtZAwwq1zmBRmc6a7gyOzVXzff7mYPzFcJF9f3d6s08Z

