from google.cloud import datastore

def add_class(ds, class_id, course, title, concepts):
    class_content = datastore.Entity(key=ds.key('class'))
    class_content.update({
    	'class_id': class_id,
    	'course': course,
    	'title': title,
    	'concepts': concepts
    })
    
    ds.put(class_content)


def add_class_with_file(ds, class_id, course, title, concepts_file):
    with open(concepts_file, 'r') as f:
        concepts = [line.strip() for line in f.readlines()]
    
        class_content = datastore.Entity(key=ds.key('class'))
        class_content.update({
    	    'class_id': class_id,
    	    'course': course,
    	    'title': title,
    	    'concepts': concepts
        })
    
        print(concepts)
        ds.put(class_content)


def get_class(ds, class_id):
    class_query = ds.query(kind='class')
    class_query.add_filter('class_id', '=', class_id)
    class_to_show = [entity for entity in class_query.fetch()][0]
    
    return class_to_show
    
    
def get_reviews(ds, class_id):
    class_query = ds.query(kind='review')
    class_query.add_filter('class_id', '=', class_id)
    class_to_show = [entity for entity in class_query.fetch()]
    
    return class_to_show
        
        
def delete_all(ds):
    q = ds.query(kind='class')
    for entity in q.fetch():
        ds.delete(entity.key)
        
    q = ds.query(kind='course')
    for entity in q.fetch():
        ds.delete(entity.key)
        
    q = ds.query(kind='review')
    for entity in q.fetch():
        ds.delete(entity.key)