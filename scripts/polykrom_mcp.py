#!/usr/bin/env python3
"""Execute Polykrom MCP requests with durable, compact evidence.

Requires Python `mcp`. A request file is a list of {tool, arguments, label?}.
Use --connect only for an inspected, owned application session. Default headless.
"""
import argparse
import asyncio
import json
import os
from datetime import timedelta
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(args):
    root=Path(__file__).resolve().parents[1]
    cli=args.cli or os.environ.get('POLYKROM_CLI','polykrom-cli')
    cli_args=['mcp','--connect',args.connect] if args.connect else ['mcp','--headless']
    if args.input: cli_args+=['--in',str(Path(args.input).resolve())]
    cli_args+=['--allow-path',str(root/'cad')]
    requests=json.loads(Path(args.requests).read_text())
    evidence=Path(args.evidence)
    evidence.parent.mkdir(parents=True,exist_ok=True)
    results=[]
    async with stdio_client(StdioServerParameters(command=cli,args=cli_args)) as (reader,writer):
        async with ClientSession(reader,writer,read_timeout_seconds=timedelta(seconds=660)) as session:
            init=await session.initialize()
            print('Server:',init.serverInfo.name,init.serverInfo.version,flush=True)
            for index,req in enumerate(requests):
                label=req.get('label',req['tool'])
                print(f'{index+1}/{len(requests)} {label}',flush=True)
                result=await session.call_tool(req['tool'],req.get('arguments',{}))
                # Image data stays in PNG files; evidence contains text and metadata.
                data=result.model_dump(mode='json',exclude_none=True)
                data['content']=[c for c in data.get('content',[]) if c.get('type')!='image']
                results.append(dict(label=label,tool=req['tool'],result=data))
                evidence.write_text(json.dumps(results,indent=2)+'\n')
                texts=[c.get('text','') for c in data['content'] if c.get('type')=='text']
                payloads=[]
                for text in texts:
                    try: payloads.append(json.loads(text))
                    except json.JSONDecodeError: pass
                rejected=any(isinstance(p,dict) and
                    (p.get('verdict')=='fail' or p.get('ok') is False) for p in payloads)
                if result.isError or rejected:
                    print('\n'.join(texts)[:3000],flush=True)
                    raise RuntimeError(f'MCP failed at {label}; inspect evidence before retrying')
                print('OK',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('requests')
    parser.add_argument('--cli')
    parser.add_argument('--connect')
    parser.add_argument('--input')
    parser.add_argument('--evidence',required=True)
    asyncio.run(run(parser.parse_args()))
