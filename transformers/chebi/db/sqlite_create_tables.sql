
CREATE TABLE compounds (
        id                  int             primary key,
        name                text            collate nocase,
        source              varchar(32)     not null,
        parent_id           int             ,
        chebi_accession     varchar(30)     not null,
        status              varchar(1)      not null,
        definition          text	    ,
        star                int             ,
        modified_on         text            ,            
        created_by          text            
);


CREATE TABLE chemical_data (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        chemical_data       text            not null,  
        source              text            not null,
        type                text            not null
);


CREATE TABLE comments (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        text                text            not null,
        created_on          timestamp(0)    not null,
        datatype            varchar(80)     ,
        datatype_id         int             not null
);


CREATE TABLE database_accession (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        accession_number    varchar(255)    not null,
        type                text            not null,
        source              text            not null
);


CREATE TABLE names (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        name                text            not null collate nocase,
        type                text            not null,
        source              text            not null,
        adapted             text            not null,
        language            text            not null 
);


CREATE TABLE reference (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        reference_id        varchar(60)     not null,
        reference_db_name   varchar(60)     not null,
        location_in_ref     varchar(90)             ,
        reference_name      varchar(1024) 
);


CREATE TABLE relation (
        id                  int             primary key,
        type                text            not null,
        init_id             int             not null
                                            references compounds(id),
        final_id            int             not null
                                            references compounds(id),
        status              varchar(1)      not null,
    unique (type,init_id,final_id)
);


CREATE TABLE structures (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        structure           text            not null,
        type                text            not null,
        dimension           text            not null,
        default_structure   varchar(1)      not null,
        autogen_structure   varchar(1)      not null
);


CREATE TABLE compound_origins (
        id                  int             primary key,
        compound_id         int             not null
                                            references compounds(id)
                                            on delete cascade,
        species_text        text            not null,
        species_accession   text                    ,
        component_text      text                    ,
        component_accession text                    ,
        strain_text         text                    ,
        source_type         text            not null,
        source_accession    text            not null,
        comments            text                    
);


