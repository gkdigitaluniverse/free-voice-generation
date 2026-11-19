import json, os, urllib.request
CK=os.environ["CK"]; U="https://connect.composio.dev/mcp"
def post(b):
    r=urllib.request.Request(U,data=json.dumps(b).encode(),method="POST",
      headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream","Authorization":"Bearer "+CK})
    raw=urllib.request.urlopen(r,timeout=180).read().decode("utf-8","ignore")
    o=[]
    for l in raw.split("\n"):
        if l.startswith("data: "):
            try:o.append(json.loads(l[6:]))
            except:pass
    return o[-1] if o else {}
post({"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"p","version":"1"}}})
def call(name,args,_id=[10]):
    _id[0]+=1
    r=post({"jsonrpc":"2.0","id":_id[0],"method":"tools/call","params":{"name":name,"arguments":args}})
    try: return json.loads(r["result"]["content"][0]["text"])
    except Exception: return r
print("=== SEARCH: github actions workflow dispatch secret ===")
s=call("COMPOSIO_SEARCH_TOOLS",{"query":"github actions workflow dispatch run logs cache repository secret"})
d=s.get("data",{})
print(json.dumps(d.get("toolkit_connection_statuses"), indent=1)[:900])
for r in d.get("results",[]):
    print("primary:", r.get("primary_tool_slugs"))
    print("related:", r.get("related_tool_slugs"))
