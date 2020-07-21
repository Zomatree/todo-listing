CREATE TABLE public.accounts (
    id bigint NOT NULL,
    username text COLLATE pg_catalog."default" NOT NULL,
    password text COLLATE pg_catalog."default" NOT NULL,
    email text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT accounts_pkey PRIMARY KEY (id)
);

CREATE TABLE public.todos (
    id bigint NOT NULL,
    title text COLLATE pg_catalog."default" NOT NULL,
    description text COLLATE pg_catalog."default" NOT NULL,
    done boolean NOT NULL DEFAULT false,
    userid bigint NOT NULL,
    CONSTRAINT todos_pkey PRIMARY KEY (id),
    CONSTRAINT foreign_userid FOREIGN KEY (userid)
        REFERENCES public.accounts (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
        NOT VALID
);

CREATE INDEX fki_foreign_userid
    ON public.todos USING btree
    (userid ASC NULLS LAST)
    TABLESPACE pg_default;