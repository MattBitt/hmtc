select id,
    name,
    size
from videofile
ORDER by created_at DESC
LIMIT 100;