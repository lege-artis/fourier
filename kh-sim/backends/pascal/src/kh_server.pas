program kh_server;
{ KH-SIM Pascal backend — KH-007
  Framework : fphttpserver (Free Pascal fcl-web low-level)
  Port      : 8005
  Endpoints : POST /simulate  GET /health  GET /info
  Note      : Uses TFPHttpServer.OnRequest directly — no module registration.
              Server.Active := True blocks in non-threaded mode (accept loop).
}
{$mode objfpc}{$H+}

uses
  SysUtils, Classes,
  fphttpserver, httpdefs,
  fpjson, jsonparser,
  kh_physics;

{ ── JSON helpers ─────────────────────────────────────────────────────────── }
function JGetD(jo: TJSONObject; const key: string; def: Double): Double;
var jd: TJSONData;
begin
  jd := jo.Find(key);
  if Assigned(jd) then Result := jd.AsFloat else Result := def;
end;

function JGetI(jo: TJSONObject; const key: string; def: Integer): Integer;
var jd: TJSONData;
begin
  jd := jo.Find(key);
  if Assigned(jd) then Result := jd.AsInteger else Result := def;
end;

procedure JAddArr(jo: TJSONObject; const key: string; const data: TRealArr);
var a: TJSONArray; k: Integer;
begin
  a := TJSONArray.Create;
  for k := 0 to Length(data)-1 do a.Add(data[k]);
  jo.Add(key, a);
end;

{ ── Request / response helpers ───────────────────────────────────────────── }
function ParseSimRequest(const body: string): TSimRequest;
var jo: TJSONObject;
begin
  jo := GetJSON(body) as TJSONObject;
  try
    Result.nx    := JGetI(jo, 'nx',    64);
    Result.ny    := JGetI(jo, 'ny',    32);
    Result.steps := JGetI(jo, 'steps', 100);
    Result.mode  := JGetI(jo, 'mode',  2);
    { Canonical defaults: match Python reference values }
    Result.lx    := JGetD(jo, 'lx',    1.0);
    Result.ly    := JGetD(jo, 'ly',    0.5);
    Result.dt    := JGetD(jo, 'dt',    0.001);
    Result.re    := JGetD(jo, 're',    1000.0);
    Result.u0    := JGetD(jo, 'u0',    1.0);
    Result.amp   := JGetD(jo, 'amp',   0.01);
  finally
    jo.Free;
  end;
end;

function BuildSimResponse(const res: TSimResult): string;
var jo, diag: TJSONObject;
begin
  jo := TJSONObject.Create;
  try
    { Nest diagnostics under "diagnostics" — mirrors Python reference schema }
    diag := TJSONObject.Create;
    diag.Add('kinetic_energy',  res.ke);
    diag.Add('enstrophy',       res.enstrophy);
    diag.Add('max_vorticity',   res.max_vort);
    diag.Add('divergence_rms',  res.div_rms);
    jo.Add('diagnostics', diag);
    jo.Add('backend',     'pascal');
    jo.Add('compute_ms',  res.compute_ms);
    JAddArr(jo, 'u',     res.u);
    JAddArr(jo, 'v',     res.v);
    JAddArr(jo, 'omega', res.omega);
    JAddArr(jo, 'psi',   res.psi);
    Result := jo.AsJSON;
  finally
    jo.Free;
  end;
end;

{ ── Handler object — owns routing; method bound to Server.OnRequest ─────── }
type
  TKhHandler = class(TObject)
  private
    procedure DoSimulate(ARequest: TFPHTTPConnectionRequest;
                         AResponse: TFPHTTPConnectionResponse);
    procedure DoHealth  (AResponse: TFPHTTPConnectionResponse);
    procedure DoInfo    (AResponse: TFPHTTPConnectionResponse);
  public
    procedure HandleRequest(Sender: TObject;
                            var ARequest: TFPHTTPConnectionRequest;
                            var AResponse: TFPHTTPConnectionResponse);
  end;

procedure TKhHandler.DoSimulate(ARequest: TFPHTTPConnectionRequest;
                                AResponse: TFPHTTPConnectionResponse);
var req: TSimRequest; res: TSimResult; msg: string;
begin
  try
    req := ParseSimRequest(ARequest.Content);
    res := kh_physics.Simulate(req);
    AResponse.Code    := 200;
    AResponse.Content := BuildSimResponse(res);
  except
    on E: Exception do begin
      msg := StringReplace(E.Message, '"', '\"', [rfReplaceAll]);
      AResponse.Code    := 400;
      AResponse.Content := Format('{"error":"%s"}', [msg]);
    end;
  end;
end;

procedure TKhHandler.DoHealth(AResponse: TFPHTTPConnectionResponse);
begin
  AResponse.Code    := 200;
  AResponse.Content := '{"status":"ok","backend":"pascal","port":8005}';
end;

procedure TKhHandler.DoInfo(AResponse: TFPHTTPConnectionResponse);
begin
  AResponse.Code    := 200;
  AResponse.Content :=
    '{"language":"Pascal","compiler":"fpc 3.2.2","framework":"fphttpserver",' +
    '"port":8005}';
end;

procedure TKhHandler.HandleRequest(Sender: TObject;
                                   var ARequest: TFPHTTPConnectionRequest;
                                   var AResponse: TFPHTTPConnectionResponse);
var path: string; qi: Integer;
begin
  AResponse.ContentType := 'application/json';
  { Strip query string from URL }
  path := ARequest.URL;
  qi   := Pos('?', path);
  if qi > 0 then path := Copy(path, 1, qi-1);
  if path = '' then path := '/';

  if (path = '/simulate') and (ARequest.Method = 'POST') then
    DoSimulate(ARequest, AResponse)
  else if path = '/health' then
    DoHealth(AResponse)
  else if path = '/info' then
    DoInfo(AResponse)
  else begin
    AResponse.Code    := 404;
    AResponse.Content := '{"error":"not found"}';
  end;
end;

{ ── Entry point ──────────────────────────────────────────────────────────── }
var
  Handler: TKhHandler;
  Server:  TFPHttpServer;

begin
  Handler := TKhHandler.Create;
  Server  := TFPHttpServer.Create(nil);
  try
    Server.Port      := 8005;
    Server.Threaded  := False;          { single-threaded accept loop }
    Server.OnRequest := @Handler.HandleRequest;
    WriteLn('kh-sim Pascal backend listening on http://0.0.0.0:8005');
    WriteLn('Press Ctrl+C to stop.');
    Server.Active := True;              { blocks — runs accept loop }
  finally
    Server.Free;
    Handler.Free;
  end;
end.
