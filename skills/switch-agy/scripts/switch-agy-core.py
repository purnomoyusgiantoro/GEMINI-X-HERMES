import os
import sys
import json
import base64
import ctypes
import ctypes.wintypes
import datetime

Advapi32 = ctypes.windll.Advapi32

class CREDENTIAL(ctypes.Structure):
    _fields_ = [
        ('Flags', ctypes.wintypes.DWORD),
        ('Type', ctypes.wintypes.DWORD),
        ('TargetName', ctypes.c_wchar_p),
        ('Comment', ctypes.c_wchar_p),
        ('LastWritten', ctypes.wintypes.FILETIME),
        ('CredentialBlobSize', ctypes.wintypes.DWORD),
        ('CredentialBlob', ctypes.POINTER(ctypes.c_byte)),
        ('Persist', ctypes.wintypes.DWORD),
        ('AttributeCount', ctypes.wintypes.DWORD),
        ('Attributes', ctypes.c_void_p),
        ('TargetAlias', ctypes.c_wchar_p),
        ('UserName', ctypes.c_wchar_p),
    ]

GEMINI_DIR = os.path.expanduser(r'~/.gemini')
PROFILES_DIR = os.path.join(GEMINI_DIR, 'profiles')
TARGET_NAME = 'gemini:antigravity'

def read_win_cred():
    pcred = ctypes.POINTER(CREDENTIAL)()
    if Advapi32.CredReadW(TARGET_NAME, 1, 0, ctypes.byref(pcred)):
        blob = ctypes.string_at(pcred.contents.CredentialBlob, pcred.contents.CredentialBlobSize)
        user_name = pcred.contents.UserName or 'antigravity'
        Advapi32.CredFree(pcred)
        try:
            return json.loads(blob.decode('utf-8')), user_name
        except Exception:
            return None, user_name
    return None, 'antigravity'

def write_win_cred(data_dict, user_name='antigravity'):
    data_str = json.dumps(data_dict)
    blob_bytes = data_str.encode('utf-8')
    blob_buf = (ctypes.c_byte * len(blob_bytes)).from_buffer_copy(blob_bytes)
    cred = CREDENTIAL()
    cred.Flags = 0
    cred.Type = 1 # Generic
    cred.TargetName = TARGET_NAME
    cred.Comment = None
    cred.CredentialBlobSize = len(blob_bytes)
    cred.CredentialBlob = ctypes.cast(blob_buf, ctypes.POINTER(ctypes.c_byte))
    cred.Persist = 2 # Local machine
    cred.AttributeCount = 0
    cred.Attributes = None
    cred.TargetAlias = None
    cred.UserName = user_name
    return bool(Advapi32.CredWriteW(ctypes.byref(cred), 0))

def delete_win_cred():
    Advapi32.CredDeleteW(TARGET_NAME, 1, 0)

def extract_email(cred_data):
    if not cred_data:
        return None
    id_tok = cred_data.get('id_token')
    if not id_tok and 'token' in cred_data:
        id_tok = cred_data['token'].get('id_token')
    if id_tok and '.' in id_tok:
        try:
            p = id_tok.split('.')[1]
            p += '=' * (-len(p) % 4)
            payload = json.loads(base64.b64decode(p).decode('utf-8'))
            return payload.get('email')
        except Exception:
            pass
    return None

def get_profile_email(slot_name):
    pdir = os.path.join(PROFILES_DIR, slot_name)
    blob_path = os.path.join(pdir, 'cred_blob.json')
    if os.path.exists(blob_path):
        try:
            with open(blob_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            em = extract_email(data)
            if em:
                return em
        except Exception:
            pass
    ga_path = os.path.join(pdir, 'google_accounts.json')
    if os.path.exists(ga_path):
        try:
            with open(ga_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if data.get('active'):
                return data['active']
        except Exception:
            pass
    return 'Belum disimpan'

def save_to_slot(slot_num, blob=None, email=None):
    slot_name = f'akun{slot_num}'
    pdir = os.path.join(PROFILES_DIR, slot_name)
    os.makedirs(pdir, exist_ok=True)
    
    if blob is None:
        blob, _ = read_win_cred()
        if not blob:
            print(f'Gagal membaca kredensial aktif dari {TARGET_NAME}.')
            return False
            
    if email is None:
        email = extract_email(blob)
        
    with open(os.path.join(pdir, 'cred_blob.json'), 'w', encoding='utf-8') as f:
        json.dump(blob, f, indent=2)
        
    other_slot = '2' if slot_num == '1' else '1'
    other_email = get_profile_email(f'akun{other_slot}')
    old_list = [other_email] if other_email != 'Belum disimpan' else []
    
    ga = {
        'active': email or 'unknown',
        'old': old_list
    }
    with open(os.path.join(pdir, 'google_accounts.json'), 'w', encoding='utf-8') as f:
        json.dump(ga, f, indent=2)
        
    token_obj = blob.get('token', {})
    oa = {
        'access_token': token_obj.get('access_token', ''),
        'refresh_token': token_obj.get('refresh_token', ''),
        'scope': 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email openid https://www.googleapis.com/auth/generative-language',
        'token_type': token_obj.get('token_type', 'Bearer'),
        'id_token': blob.get('id_token', '')
    }
    with open(os.path.join(pdir, 'oauth_creds.json'), 'w', encoding='utf-8') as f:
        json.dump(oa, f, indent=2)
        
    return True

def save_current_credentials():
    active_blob, _ = read_win_cred()
    if not active_blob:
        return
    active_email = extract_email(active_blob)
    if not active_email:
        return
        
    e1 = get_profile_email('akun1')
    e2 = get_profile_email('akun2')
    
    if active_email == e1:
        save_to_slot('1', active_blob, active_email)
    elif active_email == e2:
        save_to_slot('2', active_blob, active_email)

def do_status():
    active_blob, _ = read_win_cred()
    active_email = extract_email(active_blob) if active_blob else None
    e1 = get_profile_email('akun1')
    e2 = get_profile_email('akun2')
    
    print("\n=== STATUS AKUN AGY CLI ===")
    print(f"Akun Aktif Saat Ini : {active_email if active_email else 'Belum login'}")
    print(f"Profil Akun 1       : {e1}")
    print(f"Profil Akun 2       : {e2}")
    print("==========================\n")

def do_save(slot):
    if slot not in ('1', '2'):
        print("Error: Gunakan 'save 1' atau 'save 2'")
        return
    active_blob, _ = read_win_cred()
    if not active_blob:
        print("Tidak ada akun yang sedang aktif di Windows Credential Manager.")
        return
    email = extract_email(active_blob)
    if save_to_slot(slot, active_blob, email):
        print(f"\n[OK] Berhasil menyimpan akun aktif ({email}) ke Profil Akun {slot}!\n")

def do_setup(slot):
    if not slot:
        slot = '2'
    save_current_credentials()
    delete_win_cred()
    for f in ('google_accounts.json', 'oauth_creds.json'):
        fp = os.path.join(GEMINI_DIR, f)
        if os.path.exists(fp):
            try:
                os.remove(fp)
            except Exception:
                pass
    print(f"\n[SIAP LOGIN AKUN {slot}]")
    print("Kredensial lama telah diamankan.")
    print("Langkah selanjutnya:")
    print("1. Ketik: agy")
    print(f"2. Buka browser dan login menggunakan Akun Google ke-{slot}.")
    print("3. Setelah masuk ke agy, keluar dengan ketik: /exit")
    print(f"4. Simpan profil dengan ketik: switch-agy save {slot}\n")

def do_switch(target):
    active_blob, _ = read_win_cred()
    current_email = extract_email(active_blob) if active_blob else None
    e1 = get_profile_email('akun1')
    e2 = get_profile_email('akun2')
    
    target_slot = None
    if target in ('1', 'akun1'):
        target_slot = 'akun1'
    elif target in ('2', 'akun2'):
        target_slot = 'akun2'
    else:
        # Auto-toggle
        if current_email == e1:
            target_slot = 'akun2'
        else:
            target_slot = 'akun1'
            
    source_dir = os.path.join(PROFILES_DIR, target_slot)
    blob_path = os.path.join(source_dir, 'cred_blob.json')
    if not os.path.exists(blob_path):
        print(f"\n[PERHATIAN] Profil {target_slot} belum tersimpan!")
        print("Untuk mendaftarkan profil, jalankan:")
        print(f"  switch-agy setup {target_slot.replace('akun', '')}\n")
        return
        
    # Save current credentials before switching
    save_current_credentials()
    
    # Load target cred
    with open(blob_path, 'r', encoding='utf-8') as f:
        target_blob = json.load(f)
        
    ok = write_win_cred(target_blob)
    if not ok:
        print("\n[GAGAL] Gagal menulis kredensial ke Windows Credential Manager.")
        return
        
    # Also copy companion files to ~/.gemini
    for f in ('google_accounts.json', 'oauth_creds.json'):
        src = os.path.join(source_dir, f)
        dst = os.path.join(GEMINI_DIR, f)
        if os.path.exists(src):
            try:
                import shutil
                shutil.copyfile(src, dst)
            except Exception:
                pass
                
    new_email = extract_email(target_blob)
    print(f"\n[OK] BERHASIL BERALIH KE: {new_email} ({target_slot})")
    print("Lanjutkan obrolan Anda dengan perintah: agy -c\n")

def main():
    args = sys.argv[1:]
    cmd = args[0].lower() if args else ''
    arg = args[1].lower() if len(args) > 1 else ''
    
    if cmd == 'status':
        do_status()
    elif cmd in ('setup', 'login'):
        do_setup(arg or '2')
    elif cmd == 'save':
        do_save(arg or '1')
    elif cmd in ('1', 'akun1'):
        do_switch('akun1')
    elif cmd in ('2', 'akun2'):
        do_switch('akun2')
    else:
        # Default / auto-toggle
        do_switch('auto')

if __name__ == '__main__':
    main()
