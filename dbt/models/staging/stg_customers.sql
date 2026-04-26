WITH base AS (  
    SELECT  
        id,  
        name,  
        email,  
        created_at,  
        ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) as row_num  
    FROM raw.customers  
)  

SELECT  
    id,  
    name,  
    email,  
    created_at  
FROM base  
WHERE row_num = 1;