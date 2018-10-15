# Keypirinha launcher (keypirinha.com)

import keypirinha as kp
import keypirinha_util as kpu
import keypirinha_net as kpnet
import json
from datetime import datetime
from urllib.parse import urljoin 
import os

class Rest(kp.Plugin):
 
    TITLE='Rest'
    DESCRIPTION="rest"
    TYPE="entry"
    PREFIX="r"
    DAYS_KEEP_CACHE = 10
    LIMIT=20
    ITEMCAT = kp.ItemCategory.USER_BASE + 1

    def __init__(self):
        super().__init__()
        try:
            if os.environ['DEBUG'] == self.TITLE.lower(): 
                self._debug = True # enables self.dbg() output
        except Exception as exc:
            self._debug = False    
        self.entries = []

    def on_events(self, flags):
        """
        Reloads the package config when its changed
        """
        if flags & kp.Events.PACKCONFIG:
            self.read_config()
    
       

    def on_start(self):
        self.dbg("On Start")
        if self.read_config():
            if self.generate_cache():
                self.get_entries()

        pass

    def on_catalog(self):
        self.dbg("On catalog")
        self.set_catalog([
            self.create_item(
                category=kp.ItemCategory.KEYWORD,
                label=self.TITLE,
                short_desc=self.DESCRIPTION,
                target=self.TITLE.lower(),
                args_hint=kp.ItemArgsHint.REQUIRED,
                hit_hint=kp.ItemHitHint.KEEPALL
            )
        ])

    def on_suggest(self, user_input, items_chain):
        if not items_chain or items_chain[0].category() != kp.ItemCategory.KEYWORD:
            return
 
        suggestions = self.filter(user_input)
        self.set_suggestions(suggestions, kp.Match.ANY, kp.Sort.LABEL_ASC)

    def filter(self, user_input):
        return list(filter(lambda item: self.has_name(item, user_input), self.entries))
    
    def has_name(self, item, user_input):
        self.dbg(user_input.upper(),item.label().upper())
        if user_input.upper() in item.label().upper():
            return item
        return False

    def on_execute(self, item, action):
        if item.category() != self.ITEMCAT:
            return
        url=item.target()
        self.dbg(item.target())
        kpu.web_browser_command(private_mode=None,url=url,execute=True)

  
    def get_cache_path(self,prefix):
        cache_path = self.get_package_cache_path(True)
        return os.path.join(cache_path, prefix + self.TITLE.lower() +  '.json')


    def generate_cache(self):
        return True 
  
    def get_entries(self):
        self.dbg('Get entries')
        return self.entries

    # read ini config
    def read_config(self):
        self.dbg("Reading config")
        settings = self.load_settings()   
        return True

