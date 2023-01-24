Search.setIndex({"docnames": ["architecture", "architecture/k8s", "examples", "index", "processes", "quickstart", "runtimes", "runtimes/docker", "runtimes/eks", "runtimes/gke", "secret_stores", "secret_stores/local", "secret_stores/none", "secrets", "settings", "using-hydroplane"], "filenames": ["architecture.rst", "architecture/k8s.rst", "examples.rst", "index.rst", "processes.rst", "quickstart.rst", "runtimes.rst", "runtimes/docker.rst", "runtimes/eks.rst", "runtimes/gke.rst", "secret_stores.rst", "secret_stores/local.rst", "secret_stores/none.rst", "secrets.rst", "settings.rst", "using-hydroplane.rst"], "titles": ["Architectural Details", "How Hydroplane Interacts with Kubernetes", "Example Process Specs", "Hydroplane", "Defining Processes", "Quickstart Guide", "Runtimes", "<code class=\"docutils literal notranslate\"><span class=\"pre\">docker</span></code> - Docker (Single-Node) Runtime", "<code class=\"docutils literal notranslate\"><span class=\"pre\">eks</span></code> - Amazon EKS", "<code class=\"docutils literal notranslate\"><span class=\"pre\">gke</span></code> - Google Kubernetes Engine", "Secret Stores", "<code class=\"docutils literal notranslate\"><span class=\"pre\">local</span></code> Secret Store", "<code class=\"docutils literal notranslate\"><span class=\"pre\">none</span></code> Secret Store", "Defining Secrets", "Configuration", "Interacting with Hydroplane"], "terms": {"how": [0, 2, 3, 4, 8, 9, 14], "hydroplan": [0, 4, 5, 6, 7, 10, 11, 12, 14], "interact": [0, 3, 8, 9], "kubernet": [0, 3, 6, 8], "public": [0, 2, 3, 8, 9], "privat": [0, 3, 11], "process": [0, 3, 5, 8, 9, 14, 15], "us": [0, 3, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15], "differ": [0, 3, 6, 8, 9, 13], "servic": [0, 3, 4, 8, 9, 13], "statu": [0, 3, 8, 9], "At": 1, "thi": [1, 2, 4, 5, 6, 7, 8, 9, 11, 13, 14, 15], "point": 1, "ha": [1, 4, 5, 14], "coupl": 1, "backend": [1, 3], "ar": [1, 2, 4, 5, 7, 8, 9, 11, 13, 14, 15], "manag": [1, 4, 8, 9], "offer": [1, 8, 9], "ek": [1, 2, 3, 6, 13, 14], "gke": [1, 3, 6], "time": [1, 2, 8, 9, 15], "write": [1, 14], "document": [1, 9, 14, 15], "provid": [1, 4, 9, 11, 13, 14], "some": [1, 2, 4, 9, 11, 13], "more": [1, 3, 5, 9, 14], "detail": [1, 2, 3, 4, 15], "wai": [1, 3, 4, 6, 7, 8, 9], "reifi": 1, "variou": [1, 9], "primit": 1, "each": [1, 2, 14], "i": [1, 2, 3, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15], "run": [1, 3, 4, 5, 6, 7, 12, 13, 14, 15], "singl": [1, 3, 4, 6, 8, 9, 13], "pod": [1, 2, 8, 9], "deploy": 1, "an": [1, 3, 4, 5, 7, 9, 11, 12, 13, 14], "associ": [1, 8], "The": [1, 2, 3, 4, 7, 8, 9, 11, 12], "give": [1, 2, 4], "someth": [1, 8, 9], "expos": [1, 4, 8, 9, 15], "internet": 1, "when": [1, 4, 5, 8, 13], "ip": [1, 4, 9], "address": [1, 4, 9, 15], "easi": 1, "name": [1, 4, 7, 8, 9, 11, 12, 13, 15], "one": [1, 2, 4, 7, 8, 9, 13], "anoth": [1, 4, 7, 14], "without": [1, 7, 13], "reli": 1, "ani": [1, 2, 4, 7, 8, 9, 10, 12, 13], "kind": [1, 15], "third": 1, "parti": 1, "discoveri": 1, "mechan": 1, "ensur": [1, 4], "keep": 1, "": [1, 2, 4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15], "schedul": 1, "even": [1, 13], "preempt": 1, "evict": 1, "contain": [1, 2, 3, 4, 6, 7, 9, 13], "actual": 1, "If": [1, 3, 4, 8, 15], "you": [1, 2, 4, 5, 7, 8, 9, 11, 12, 13, 14, 15], "want": [1, 2, 4, 8, 9, 13], "familiar": [1, 8], "yourself": 1, "d": [1, 4], "recommend": 1, "articl": 1, "matthew": 1, "palmer": 1, "onli": [1, 15], "need": [1, 3, 7, 8, 10, 12, 13, 14], "routabl": [1, 4, 9], "discover": 1, "within": [1, 8, 9, 13], "cluster": [1, 3, 14], "so": [1, 2, 4, 8, 9, 14], "clusterip": 1, "from": [1, 2, 3, 4, 5, 8, 9, 14], "outsid": [1, 4, 9], "we": [1, 2, 8, 9], "have": [1, 2, 4, 7, 8, 9, 13], "handl": 1, "them": [1, 2, 7, 9, 13], "separ": [1, 5, 8, 9, 13], "In": [1, 2, 5, 6, 8, 9], "typic": 1, "where": [1, 8], "back": [1, 8, 9, 15], "auto": [1, 9], "scale": 1, "collect": 1, "put": [1, 8], "loadbalanc": 1, "front": 1, "load": [1, 5], "balanc": 1, "traffic": 1, "between": 1, "our": [1, 9], "case": 1, "re": [1, 2, 4, 5, 8, 9, 12], "expect": 1, "higher": 1, "level": 1, "than": [1, 4, 14], "do": [1, 8, 9, 11], "thing": [1, 8, 14], "like": [1, 4, 8, 9, 10, 11, 12, 13, 14], "individu": [1, 8], "were": 1, "creat": [1, 2, 3, 4, 13, 15], "per": [1, 2], "also": [1, 9, 14, 15], "cloud": [1, 3, 4, 9], "particularli": 1, "aw": [1, 3, 14], "realli": 1, "expens": 1, "To": [1, 8, 9, 11, 13, 14, 15], "avoid": 1, "cost": [1, 4], "overhead": 1, "nodeport": 1, "rout": [1, 9], "A": [1, 3, 4, 13], "high": 1, "number": [1, 4], "port": [1, 2, 4, 8, 9, 13, 15], "everi": [1, 4, 9, 14], "node": [1, 3, 6], "all": [1, 4, 9, 14, 15], "transpar": 1, "overlai": 1, "network": [1, 7, 9], "doe": [1, 3, 12], "what": [1, 11], "addit": 1, "resourc": [1, 4], "make": [1, 3, 4, 5, 8, 9], "look": [1, 2, 8, 11, 15], "client": [1, 2, 9], "perspect": 1, "though": 1, "onc": [1, 4, 8, 9, 11], "inconsist": 1, "abstract": [1, 3, 4], "list": [1, 2, 3, 5, 8, 9, 13, 15], "oper": 1, "present": 1, "maintain": 1, "illus": 1, "access": [1, 8, 9, 10, 13], "introspect": 1, "determin": 1, "treat": 1, "can": [1, 2, 4, 8, 9, 10, 11, 13, 14, 15], "veri": [1, 11], "quickli": [1, 5], "sometim": [1, 13], "mai": [1, 4], "take": 1, "while": [1, 8], "start": [1, 2, 3, 5, 7, 8, 9, 15], "after": [1, 8, 9], "successfulli": 1, "submit": 1, "spec": [1, 3, 4, 15], "usual": [1, 4], "delai": 1, "creation": 1, "caus": 1, "pressur": 1, "doesn": [1, 4, 6, 7, 9, 12], "t": [1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15], "enough": [1, 8, 10, 11, 13], "remain": 1, "accommod": 1, "up": [1, 2, 3, 7, 8, 15], "acquir": 1, "those": [1, 3, 4, 6, 8, 13, 15], "mean": [1, 4], "readi": [1, 2], "should": [1, 2, 4, 5, 8, 9, 11, 15], "abl": [1, 8, 9], "accept": [1, 8], "connect": [1, 3, 9], "other": [1, 2, 4, 13], "file": [2, 4, 5, 7, 8, 9, 11, 14], "nginx": [2, 4, 5, 8, 9], "json": [2, 5, 8, 9, 13, 15], "simpl": [2, 3, 4, 5, 7, 8, 9, 15], "hello": [2, 4, 5, 8, 9, 11], "world": [2, 4, 5, 8, 9, 11], "webserv": 2, "root": [2, 5, 8, 9, 11], "repo": [2, 5, 8, 9], "bin": [2, 5, 8, 9, 11, 14, 15], "hpctl": [2, 3, 5, 8, 9], "code": 2, "block": [2, 8], "below": [2, 4], "denot": 2, "command": [2, 3, 4, 9, 11], "rest": [2, 15], "output": 2, "process_nam": [2, 4, 8, 9, 13], "group": [2, 3, 8, 9, 15], "null": [2, 8, 9], "socket_address": [2, 8, 9], "host": [2, 4, 8, 9, 15], "0": [2, 3, 4, 8], "8080": [2, 5], "is_publ": [2, 8, 9], "true": [2, 4, 8, 9, 11], "2022": [2, 8, 9], "12": [2, 5, 8, 9], "01t20": 2, "25": 2, "36": 2, "009608": 2, "00": [2, 8, 9], "note": [2, 3, 9], "concat": 2, "togeth": [2, 3], "open": [2, 5, 8, 9], "http": [2, 5, 8, 9, 15], "ve": [2, 8, 9], "got": [2, 8, 9], "jq": [2, 8, 9], "maco": [2, 5, 8, 9], "liner": [2, 8, 9], "r": [2, 8, 9], "tostr": [2, 8, 9], "three": 2, "two": [2, 4, 8, 13, 14], "found": [2, 9], "hydroflow": 2, "warm": 2, "sleep": 2, "5": [2, 4, 14], "alic": 2, "bob": 2, "don": [2, 4, 9, 10, 11, 13], "interfac": [2, 6], "ll": [2, 8, 9, 11], "log": [2, 9], "thei": [2, 4, 13], "docker": [2, 3, 4, 5, 6, 10, 12, 13, 14], "runtim": [2, 3, 4, 8, 9, 11, 12, 13, 14], "check": [2, 5], "exist": [2, 6], "see": [2, 5, 8, 9, 13, 14], "p": 2, "report": 2, "both": [2, 4, 13], "send": 2, "random": 2, "messag": 2, "kubectl": 2, "get": [2, 5, 7, 8, 9, 11, 15], "g": [2, 4, 8, 14, 15], "launch": [3, 4, 5, 8, 9], "container": 3, "infrastructur": [3, 7], "meant": [3, 7, 11], "act": [3, 6, 9], "unifi": 3, "api": [3, 9], "stop": [3, 4, 5, 8, 9, 15], "deploi": 3, "multipl": 3, "much": 3, "complex": 3, "possibl": [3, 5], "quickstart": [3, 15], "guid": [3, 7, 15], "line": [3, 9], "tool": [3, 9], "know": [3, 4], "which": [3, 4, 7, 9], "server": [3, 4, 5, 8, 9], "talk": [3, 8], "configur": [3, 4], "exampl": [3, 4, 5, 13], "defin": [3, 8, 15], "specif": [3, 14], "cull": [3, 14], "set": [3, 4, 11, 12, 13, 14], "amazon": [3, 6], "step": 3, "1": [3, 4], "iam": 3, "user": [3, 11], "2": [3, 14], "3": [3, 5], "implement": 3, "authent": [3, 4, 10, 11, 13], "permiss": 3, "refer": [3, 4, 7, 9, 13, 15], "googl": [3, 6], "engin": [3, 6], "your": [3, 4, 5, 7, 8, 11, 14], "environ": [3, 4, 13, 15], "vpc": 3, "4": 3, "gcp": 3, "secret": [3, 4, 7, 8, 9, 14], "relat": [3, 8], "store": [3, 7, 8, 9, 13, 14], "local": [3, 7, 8, 9, 10, 14], "snippet": 3, "initi": [3, 5, 8], "ad": [3, 8], "longer": 3, "remov": 3, "none": [3, 4, 7, 8, 9, 10, 11, 13, 14], "architectur": 3, "web": 3, "sure": [3, 4, 5, 8, 9], "It": [3, 11, 12, 13], "work": [3, 5, 8, 9], "chat": 3, "respons": 4, "destroi": [4, 8, 15], "anyth": 4, "insid": [4, 9], "short": 4, "describ": 4, "specifi": [4, 7, 9, 15], "locat": [4, 9, 11], "imag": 4, "here": [4, 7, 8, 9, 11, 12, 13, 14], "test": [4, 5, 9, 14], "image_uri": [4, 13], "nginxdemo": 4, "container_port": [4, 13], "80": [4, 13], "host_port": 4, "9090": 4, "protocol": 4, "tcp": 4, "displai": 4, "webpag": 4, "most": [4, 8, 9, 10, 13, 15], "option": [4, 8, 11, 13, 14], "abil": [4, 8], "chang": [4, 11], "lot": 4, "its": [4, 5, 6, 9, 11, 14], "descript": 4, "format": [4, 11], "pydant": [4, 7, 8, 9, 11, 12, 13], "model": [4, 7, 8, 9, 11, 12, 13], "process_spec": 4, "processspec": 4, "processs": 4, "field": [4, 7, 8, 9, 11, 12, 13], "str": [4, 8, 9, 13], "requir": [4, 8, 9, 10, 11, 13], "belong": 4, "containerspec": 4, "has_public_ip": 4, "bool": 4, "fals": 4, "publicli": 4, "container_spec": 4, "valid": [4, 8], "requests_cannot_exceed_limit": 4, "resource_limit": 4, "uri": 4, "fulli": [4, 8], "qualifi": [4, 8], "shorthand": 4, "e": [4, 8, 14, 15], "python": [4, 5], "usernam": [4, 13], "union": 4, "processsecret": [4, 13], "registri": [4, 13], "password": [4, 8, 11, 13], "portmap": 4, "env": [4, 13], "environmentvari": 4, "variabl": [4, 13, 15], "given": [4, 8, 15], "resource_request": 4, "resourcespec": 4, "request": [4, 8, 15], "physic": 4, "alloc": 4, "limit": 4, "amount": 4, "allow": [4, 7, 9], "consum": 4, "exce": 4, "valu": [4, 13], "liter": [4, 7, 8, 9, 11, 12], "default_host_port": 4, "constrainedintvalu": [4, 8], "listen": 4, "constraint": [4, 8, 11], "minimum": [4, 8], "maximum": [4, 8], "65535": 4, "honor": 4, "portprotocol": 4, "spoken": 4, "bound": 4, "bind": [4, 8], "pass": [4, 13, 14], "isn": [4, 15], "class": 4, "enumer": 4, "encapsul": 4, "either": [4, 8, 9], "cpu_vcpu": 4, "constraineddecimalvalu": 4, "vcpu": 4, "001": 4, "memory_mib": 4, "mib": 4, "memori": 4, "made": 4, "part": 4, "well": [4, 11], "itself": [4, 6, 11, 13], "stateless": 4, "interrog": 4, "vari": 4, "annot": 4, "tag": 4, "distinguish": 4, "By": [4, 9, 11, 14], "default": [4, 5, 8, 9, 11, 12, 14, 15], "commun": [4, 6, 8], "often": 4, "cannot": 4, "control": 4, "whether": 4, "instead": [4, 6, 13], "experi": 4, "monei": 4, "leav": 4, "sit": 4, "around": [4, 13], "accident": 4, "culler": [4, 14], "automat": [4, 8, 9, 15], "older": [4, 14], "certain": [4, 8], "ag": 4, "minut": [4, 14], "show": 4, "secret_stor": [4, 7, 8, 9, 11, 12, 14], "secret_store_typ": [4, 7, 8, 9, 11, 12, 14], "runtime_typ": [4, 7, 8, 9, 14], "process_cul": [4, 14], "hour": [4, 14], "max_age_minut": [4, 14], "120": [4, 14], "culling_interval_minut": [4, 14], "util": 4, "int": 4, "frequenc": 4, "zero": 5, "been": 5, "monterei": 5, "minim": [5, 7], "modif": 5, "recent": 5, "version": 5, "linux": 5, "download": 5, "instal": [5, 8, 9], "desktop": 5, "www": 5, "com": 5, "product": [5, 11], "app": 5, "machin": [5, 9], "clone": 5, "enter": [5, 8, 11], "git": 5, "github": 5, "hydro": [5, 8, 9], "project": [5, 8, 9], "cd": 5, "10": 5, "later": 5, "python3": 5, "poetri": 5, "haven": [5, 8, 9], "alreadi": [5, 8, 9], "org": [5, 9], "doc": [5, 9, 15], "info": [5, 11], "curl": [5, 9], "ssl": 5, "virtualenv": 5, "depend": 5, "shell": 5, "basic": [5, 14], "config": [5, 8, 9, 14], "yml": [5, 8, 9, 14], "termin": [5, 8, 9], "print": 5, "sinc": [5, 7], "first": [5, 8, 9, 15], "let": [5, 8, 9], "localhost": [5, 15], "browser": [5, 8, 9], "page": [5, 8, 9], "finish": 5, "noth": [5, 8, 12], "left": 5, "pre": 6, "behalf": [6, 9], "common": 6, "varieti": 6, "bunch": 7, "Its": 7, "pretti": 7, "just": [7, 9], "daemon": 7, "bridg": 7, "dn": 7, "substant": 7, "still": 7, "follow": [7, 8, 9, 15], "integr": [8, 9], "awscredenti": 8, "cluster_nam": [8, 14], "region": [8, 9, 14], "u": [8, 9, 14], "west": [8, 14], "namespac": [8, 9], "my": [8, 9, 11, 13, 15], "cool": 8, "store_loc": [8, 11, 14], "hydro_secret": [8, 11, 14], "access_kei": [8, 14], "access_key_id": [8, 14], "secret_nam": [8, 13, 14], "kei": [8, 11, 13, 14], "accesskeyid": [8, 14], "secret_access_kei": [8, 14], "secretaccesskei": [8, 14], "order": [8, 10, 13], "setup": [8, 13], "instruct": [8, 9], "section": [8, 14], "readm": 8, "come": 8, "done": 8, "assum": [8, 9], "wa": [8, 9], "subsequ": 8, "breviti": 8, "admin": 8, "add": [8, 9, 11], "init": [8, 11], "now": [8, 9], "call": [8, 9, 15], "cred": 8, "id": [8, 9], "f": [8, 11], "delet": [8, 11, 15], "plaintext": 8, "origin": 8, "afterward": 8, "rm": 8, "final": [8, 9], "c": [8, 9, 14], "prompt": [8, 11], "empti": [8, 9], "becaus": [8, 9], "yet": [8, 9], "try": [8, 9], "remot": [8, 9], "34": [8, 9], "217": [8, 9], "208": [8, 9], "197": [8, 9], "31491": [8, 9], "01t22": [8, 9], "40": [8, 9], "33": [8, 9], "otherwis": [8, 9], "copi": [8, 9], "past": [8, 9, 11], "window": [8, 9], "verifi": [8, 9], "everyth": [8, 9], "For": [8, 9, 10, 13], "must": 8, "correspond": 8, "These": 8, "object": [8, 13], "xxxxxxxxx": 8, "xxxxxxx": 8, "referenc": 8, "directli": [8, 15], "gener": [8, 15], "consid": 8, "best": 8, "practic": 8, "temporari": 8, "expir": 8, "period": [8, 9], "attempt": 8, "renew": 8, "abov": [8, 9, 11, 14], "eksadmin": 8, "last": 8, "assume_rol": 8, "role_arn": 8, "arn": 8, "123456789012": 8, "script": [8, 15], "appropri": [8, 9], "privileg": 8, "awsaccesskei": 8, "pair": 8, "hydroplanesecret": [8, 13], "awsassumerol": 8, "inform": [8, 9, 13, 14], "necessari": 8, "princip": 8, "temporarili": 8, "external_id": 8, "extern": 8, "session_nam": 8, "session": 8, "session_duration_second": 8, "900": 8, "durat": 8, "second": 8, "43200": 8, "cluster_id": 9, "whcih": 9, "develop": [9, 11], "central1": 9, "substitut": 9, "gcloud": 9, "login": 9, "auth": 9, "next": 9, "applic": 9, "credenti": [9, 10, 13, 14], "comput": 9, "subnet": 9, "mode": 9, "mtu": 9, "1460": 9, "bgp": 9, "aren": [9, 11], "poke": 9, "hole": 9, "firewal": 9, "rule": 9, "direct": 9, "ingress": 9, "prioriti": 9, "999": 9, "action": [9, 13], "sourc": 9, "rang": 9, "ipifi": 9, "32": 9, "similar": 9, "declar": 9, "whatev": 9, "autopilot": 9, "minutia": 9, "fill": 9, "blank": 9, "releas": 9, "channel": 9, "regular": 9, "global": 9, "subnetwork": 9, "ipv4": 9, "cidr": 9, "17": 9, "22": 9, "adc": 9, "strategi": 9, "librari": 9, "avail": [9, 13], "about": 9, "popul": 9, "pick": 9, "refresh": 9, "shouldn": 9, "again": 9, "retriev": [10, 13, 15], "filesystem": 11, "symetr": 11, "encrypt": 11, "good": 11, "experiment": 11, "path": 11, "secretstr": 11, "NOT": 11, "edit": 11, "overwritten": 11, "type": 11, "string": [11, 13], "writeonli": 11, "flag": [11, 14, 15], "might": [11, 13], "token": 11, "long": 11, "complic": 11, "certif": 11, "lend": 11, "themselv": 11, "being": 11, "input": 11, "filenam": 11, "echo": 11, "txt": 11, "As": 12, "impli": 12, "ask": 12, "throw": 12, "error": 12, "nice": 12, "desir": 13, "data": 13, "newlin": 13, "special": 13, "charact": 13, "conveni": 13, "same": [13, 14], "whose": 13, "content": 13, "cleartext": 13, "foo": [13, 15], "bar": 13, "ultra_secret_thingi": 13, "ultra": 13, "yaml": 14, "conf": 14, "read": 14, "own": 14, "There": 14, "over": 15, "serv": 15, "date": 15, "represent": 15, "rough": 15, "outlin": 15, "method": 15, "post": 15, "bodi": 15, "serial": 15, "particular": 15, "programmat": 15, "hassl": 15, "wrapper": 15, "hide": 15, "behind": 15, "cli": 15, "current": 15, "hydroplane_serv": 15, "fall": 15, "8000": 15, "explicitli": 15, "hydroserv": 15, "4040": 15}, "objects": {"hydroplane.models": [[8, 0, 0, "-", "aws"], [4, 0, 0, "-", "container_spec"], [4, 0, 0, "-", "process_spec"]], "hydroplane.models.aws": [[8, 1, 1, "", "AWSAccessKey"], [8, 1, 1, "", "AWSAssumeRole"], [8, 1, 1, "", "AWSCredentials"]], "hydroplane.models.aws.AWSAccessKey": [[8, 2, 1, "", "access_key_id"], [8, 2, 1, "", "secret_access_key"]], "hydroplane.models.aws.AWSAssumeRole": [[8, 2, 1, "", "external_id"], [8, 2, 1, "", "role_arn"], [8, 2, 1, "", "session_duration_seconds"], [8, 2, 1, "", "session_name"]], "hydroplane.models.aws.AWSCredentials": [[8, 2, 1, "", "access_key"], [8, 2, 1, "", "assume_role"]], "hydroplane.models.container_spec": [[4, 1, 1, "", "ContainerSpec"], [4, 1, 1, "", "EnvironmentVariable"], [4, 1, 1, "", "PortMapping"], [4, 4, 1, "", "PortProtocol"], [4, 1, 1, "", "ResourceSpec"]], "hydroplane.models.container_spec.ContainerSpec": [[4, 2, 1, "", "command"], [4, 2, 1, "", "env"], [4, 2, 1, "", "image_uri"], [4, 2, 1, "", "password"], [4, 2, 1, "", "ports"], [4, 3, 1, "", "requests_cannot_exceed_limits"], [4, 2, 1, "", "resource_limit"], [4, 2, 1, "", "resource_request"], [4, 2, 1, "", "username"]], "hydroplane.models.container_spec.EnvironmentVariable": [[4, 2, 1, "", "name"], [4, 2, 1, "", "value"]], "hydroplane.models.container_spec.PortMapping": [[4, 2, 1, "", "container_port"], [4, 3, 1, "", "default_host_port"], [4, 2, 1, "", "host_port"], [4, 2, 1, "", "name"], [4, 2, 1, "", "protocol"]], "hydroplane.models.container_spec.ResourceSpec": [[4, 2, 1, "", "cpu_vcpu"], [4, 2, 1, "", "memory_mib"]], "hydroplane.models.process_spec": [[4, 1, 1, "", "ProcessSpec"]], "hydroplane.models.process_spec.ProcessSpec": [[4, 2, 1, "", "container"], [4, 2, 1, "", "group"], [4, 2, 1, "", "has_public_ip"], [4, 2, 1, "", "process_name"]], "hydroplane.models.secret": [[13, 1, 1, "", "HydroplaneSecret"], [13, 1, 1, "", "ProcessSecret"]], "hydroplane.models.secret.HydroplaneSecret": [[13, 2, 1, "", "key"], [13, 2, 1, "", "secret_name"]], "hydroplane.models.secret.ProcessSecret": [[13, 2, 1, "", "key"], [13, 2, 1, "", "secret_name"]], "hydroplane.runtimes.docker": [[7, 1, 1, "", "Settings"]], "hydroplane.runtimes.docker.Settings": [[7, 2, 1, "", "runtime_type"]], "hydroplane.runtimes.eks": [[8, 1, 1, "", "Settings"]], "hydroplane.runtimes.eks.Settings": [[8, 2, 1, "", "cluster_name"], [8, 2, 1, "", "credentials"], [8, 2, 1, "", "namespace"], [8, 2, 1, "", "region"], [8, 2, 1, "", "runtime_type"]], "hydroplane.runtimes.gke": [[9, 1, 1, "", "Settings"]], "hydroplane.runtimes.gke.Settings": [[9, 2, 1, "", "cluster_id"], [9, 2, 1, "", "namespace"], [9, 2, 1, "", "project"], [9, 2, 1, "", "region"], [9, 2, 1, "", "runtime_type"]], "hydroplane.secret_stores.local": [[11, 1, 1, "", "Settings"]], "hydroplane.secret_stores.local.Settings": [[11, 2, 1, "", "password"], [11, 2, 1, "", "secret_store_type"], [11, 2, 1, "", "store_location"]], "hydroplane.secret_stores.none": [[12, 1, 1, "", "Settings"]], "hydroplane.secret_stores.none.Settings": [[12, 2, 1, "", "secret_store_type"]], "hydroplane.utils.process_culler": [[4, 1, 1, "", "Settings"]], "hydroplane.utils.process_culler.Settings": [[4, 2, 1, "", "culling_interval_minutes"], [4, 2, 1, "", "max_age_minutes"]]}, "objtypes": {"0": "py:module", "1": "py:pydantic_model", "2": "py:pydantic_field", "3": "py:pydantic_validator", "4": "py:class"}, "objnames": {"0": ["py", "module", "Python module"], "1": ["py", "pydantic_model", "Python model"], "2": ["py", "pydantic_field", "Python field"], "3": ["py", "pydantic_validator", "Python validator"], "4": ["py", "class", "Python class"]}, "titleterms": {"architectur": 0, "detail": [0, 8, 9], "how": [1, 15], "hydroplan": [1, 3, 8, 9, 13, 15], "interact": [1, 15], "kubernet": [1, 9], "public": [1, 4], "privat": [1, 4], "process": [1, 2, 4, 13], "us": 1, "differ": 1, "servic": 1, "statu": 1, "exampl": [2, 7, 8, 9, 11, 12, 14], "spec": 2, "content": [2, 3, 8, 9, 11, 15], "web": 2, "server": [2, 15], "launch": 2, "make": 2, "sure": 2, "It": 2, "work": 2, "stop": 2, "chat": 2, "defin": [4, 13], "specif": 4, "group": [4, 13], "list": 4, "cull": 4, "quickstart": [5, 7, 8, 9], "guid": 5, "runtim": [6, 7, 10], "avail": [6, 10], "docker": 7, "singl": 7, "node": 7, "set": [7, 8, 9], "configur": [7, 8, 9, 11, 12, 14], "ek": 8, "amazon": 8, "step": [8, 9], "1": [8, 9], "creat": [8, 9], "an": 8, "cluster": [8, 9], "iam": 8, "user": 8, "2": [8, 9], "3": [8, 9], "run": [8, 9], "implement": [8, 9], "authent": [8, 9], "aw": 8, "credenti": 8, "role": 8, "assumpt": 8, "A": 8, "note": 8, "permiss": 8, "refer": 8, "gke": 9, "googl": 9, "engin": 9, "0": 9, "up": 9, "your": 9, "environ": 9, "vpc": 9, "If": 9, "need": 9, "4": 9, "gcp": 9, "secret": [10, 11, 12, 13], "store": [10, 11, 12], "local": 11, "snippet": [11, 12], "initi": 11, "ad": 11, "simpl": 11, "longer": 11, "more": 11, "complex": 11, "remov": 11, "from": 11, "none": 12, "relat": 13, "togeth": 13, "The": 15, "api": 15, "command": 15, "line": 15, "tool": 15, "hpctl": 15, "doe": 15, "know": 15, "which": 15, "talk": 15}, "envversion": {"sphinx.domains.c": 2, "sphinx.domains.changeset": 1, "sphinx.domains.citation": 1, "sphinx.domains.cpp": 6, "sphinx.domains.index": 1, "sphinx.domains.javascript": 2, "sphinx.domains.math": 2, "sphinx.domains.python": 3, "sphinx.domains.rst": 2, "sphinx.domains.std": 2, "sphinx": 56}})