import json

class SMTInstructionPacker:
    def __init__(self, manifest_path):
        with open(manifest_path, 'r') as f:
            self.manifest = json.load(f)["hardware"]
        self.unit_fields_cache = {u["name"].upper(): u["fields"] for u in self.manifest["units"]}

    def pack_instruction_parallel(self, ids_in_slot, all_instructions, global_data, total_bits=128):
        """🟢 AOS P3.3: Parallel VLIW Packing (Header + Multiple Unit Payloads)"""
        
        # 1. Base Header Construction (Common to all merged instructions)
        # Shared fields: vld, loops, inc, dly, embed
        header_val = 0
        header_val |= (int(global_data.get('vld', 1)) & 0x1) << 40
        header_val |= (int(global_data.get('dly', 0)) & 0x1F) << 25
        header_val |= (int(global_data.get('loops', 0)) & 0xFF) << 11
        header_val |= (int(global_data.get('inc', 0)) & 0x7FF) # AX_03: Shared INC
        
        full_packet = header_val << (total_bits - 41)
        
        # 2. Parallel Payload Merging: Iterate through all instructions in this cycle
        for i_id in ids_in_slot:
            inst_obj = next(i for i in all_instructions if i["id"] == i_id)
            unit_name = inst_obj["unit"].upper()
            
            if unit_name in self.unit_fields_cache:
                fields = self.unit_fields_cache[unit_name]
                unit_payload = 0
                for field in fields:
                    f_bits = field['bits']
                    f_val = inst_obj.get(field['name'], field.get('default', 0))
                    # Special Case: vld bit inside unit field should be set
                    if field['name'] == 'vld': f_val = 1
                    unit_payload = (unit_payload << f_bits) | (int(f_val) & ((1 << f_bits) - 1))
                
                # Each unit might have a predestined offset in the 'CODE' field if not dynamic
                # For this incremental step, we assume sequential packing or manifest-driven pos
                # Logic: Find 'pos' in manifest if available
                first_field = fields[0]
                bit_pos = first_field.get('pos', 0) # Use 'pos' from manifest if it exists
                
                # Shift unit payload to its dedicated physical position
                # (Simplified: we'll use a mapping or just Or it if pos is defined)
                full_packet |= (unit_payload << bit_pos)
        
        hex_str = hex(full_packet)[2:].zfill(total_bits // 4)
        return hex_str.upper()

if __name__ == "__main__":
    # Test-lite within module
    packer = SMTInstructionPacker("flow/02_Specs/Hardware_Manifest.json")
    # Test a Logic instruction with DLY=5
    test_inst = {"unit": "LOGIC", "vld": 1, "dly": 5, "inst_typ": 4} # copy
    print(f"Sample Hex: {packer.pack_instruction(test_inst)}")
