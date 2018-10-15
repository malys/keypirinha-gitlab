# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json
from datetime import datetime
from urllib.parse import urljoin 
import os
from .lib.rest import Rest 

class Gitlab(Rest):
 
    TITLE='Gitlab'
    DESCRIPTION="Search projects"
    TYPE="project"
    PREFIX="p"
    LIMIT=20

    def generate_cache(self):
        self.dbg("generate_cache user",self.TOKEN,self.DOMAIN) 
        cache_path_c = self.get_cache_path(self.PREFIX)
        should_generate = False
        cache_path = self.get_package_cache_path(True)
        self.dbg(cache_path) 

        for i in os.listdir(cache_path):
            self.dbg('Find',i) 
            if os.path.isfile(os.path.join(cache_path,i)) and (self.PREFIX + self.TITLE.lower())  in i:
                file = os.path.join(cache_path,i)
                self.dbg('file',file)
                break
        
        try:
            last_modified = datetime.fromtimestamp(os.path.getmtime(file)).date()
            if ((last_modified - datetime.today().date()).days > self.DAYS_KEEP_CACHE):
                should_generate = True
        except Exception as exc:
            should_generate = True

        if not should_generate:
            return True
        opener = kpnet.build_urllib_opener()
        urlChannels= urljoin(self.DOMAIN ,'/api/v4/projects?owned=true&per_page=100&private_token=' + self.TOKEN)

        offset=1
        total= self.LIMIT
        while offset < total:
            try:
                with opener.open(urlChannels + '&page=' + str(offset)) as request:
                    response = request.read()
                    data = json.loads(response)
                    if len(data)<10:
                        total=offset
                    self.dbg(offset,total)  
                    with open(self.get_cache_path(str(offset) +self.PREFIX), "w") as index_file:
                        json.dump(data, index_file, indent=2)
                        offset= offset + 1 
            except Exception as exc:
                self.err("Could not reach the entries to generate the cache: ", exc)  
                return (offset>0) 
  

    def get_entries(self):
        self.dbg('Get entries')
        if not self.entries:
            cache_path = self.get_package_cache_path(True)
            for i in os.listdir(cache_path):
                self.dbg(i)
                if os.path.isfile(os.path.join(cache_path,i)) and (self.PREFIX + self.TITLE.lower()) in i:
                    with open(os.path.join(cache_path,i), "r") as users_file:
                        data = json.loads(users_file.read())
                        for item in data:
                            self.dbg('projects:' ,item['name']) 
                            #self.dbg("-------------------------") 
                            suggestion = self.create_item(
                                category=self.ITEMCAT,
                                label=item['name'],
                                short_desc=self.TYPE,
                                target=item['http_url_to_repo'],
                                args_hint=kp.ItemArgsHint.FORBIDDEN,
                                hit_hint=kp.ItemHitHint.IGNORE
                            )
                            self.entries.append(suggestion)    

        self.dbg('Length:' , len(self.entries) )
        return self.entries

    # read ini config
    def read_config(self):
        self.dbg("Reading config")
        settings = self.load_settings()

        self.TOKEN = str(settings.get("TOKEN", "main"))
        self.DOMAIN = str(settings.get("DOMAIN", "main"))

        if not self.DOMAIN or not self.TOKEN :
            self.dbg("Not configured",self.DOMAIN,self.TOKEN)
            return False   
        return True
