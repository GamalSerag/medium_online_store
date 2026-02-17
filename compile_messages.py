
import struct
import array
import os

def generate():
    """
    Generate binary .mo file from .po file.
    """
    infile = 'locale/ar/LC_MESSAGES/django.po'
    outfile = 'locale/ar/LC_MESSAGES/django.mo'

    if not os.path.exists(infile):
        print(f"Error: {infile} not found.")
        return

    # Parse .po file
    messages = {}
    current_msgid = None
    current_msgstr = None
    buffer = []
    state = 'none' # none, msgid, msgstr

    print(f"Reading {infile}...")
    try:
        with open(infile, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except UnicodeDecodeError:
        print("Error: content is not utf-8 encoded.")
        return

    for line in lines:
        line = line.strip()
        
        if not line or line.startswith('#'):
            if state == 'msgstr' and current_msgid is not None:
                current_msgstr = ''.join(buffer)
                messages[current_msgid] = current_msgstr
                current_msgid = None
                state = 'none'
            continue

        if line.startswith('msgid "'):
            # If we were parsing a previous message and hit a new one without empty lines
            if state == 'msgstr' and current_msgid is not None:
                current_msgstr = ''.join(buffer)
                messages[current_msgid] = current_msgstr
                current_msgid = None

            state = 'msgid'
            buffer = [line[7:-1]]
        
        elif line.startswith('msgstr "'):
            if state == 'msgid':
                current_msgid = ''.join(buffer)
            state = 'msgstr'
            buffer = [line[8:-1]]
            
        elif line.startswith('"'):
            buffer.append(line[1:-1])

    # Add last entry
    if state == 'msgstr' and current_msgid is not None:
        current_msgstr = ''.join(buffer)
        messages[current_msgid] = current_msgstr

    # Remove empty header if present as regular message (it's metadata)
    # But keep it if needed for gettext to parse charset
    # Actually, gettext needs the empty string key for metadata.
    # Let's clean up escapes
    
    clean_messages = {}
    for k, v in messages.items():
        if k is None or v is None:
            continue
        k = k.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
        v = v.replace('\\n', '\n').replace('\\"', '"').replace('\\t', '\t')
        clean_messages[k] = v

    print(f"Found {len(clean_messages)} messages.")

    # Generate .mo binary format
    # The format is:
    # magic number
    # revision
    # number of strings
    # offset of table with original strings
    # offset of table with translation strings
    # size of hashing table
    # offset of hashing table
    
    keys = sorted(clean_messages.keys())
    offsets = []
    ids = b''
    strs = b''
    
    for id in keys:
        # For each string, we need to store:
        # length, offset
        
        id_encoded = id.encode('utf-8')
        str_encoded = clean_messages[id].encode('utf-8')
        
        offsets.append((len(ids), len(id_encoded), len(strs), len(str_encoded)))
        
        ids += id_encoded + b'\0'
        strs += str_encoded + b'\0'

    # offsets
    keystart = 7 * 4 + 16 * len(keys)
    valuestart = keystart + len(ids)
    
    koffsets = []
    voffsets = []
    
    for o1, l1, o2, l2 in offsets:
        koffsets += [l1, o1 + keystart]
        voffsets += [l2, o2 + valuestart]
        
    output = struct.pack('Iiiiiii',
                         0x950412de,        # Magic
                         0,                 # Version
                         len(keys),         # N strings
                         28,                # Offset of keys (7 * 4)
                         28 + len(keys) * 8, # Offset of values
                         0,                 # Size of hash table
                         0                  # Offset of hash table
                         )
    
    output += array.array("i", koffsets).tobytes()
    output += array.array("i", voffsets).tobytes()
    output += ids
    output += strs
    
    with open(outfile, 'wb') as f:
        f.write(output)
        
    print(f"Successfully compiled {len(keys)} messages to {outfile}")

if __name__ == "__main__":
    generate()
