import os
import json

class Agent:
    def __init__(self):
        self.last_tool_call = None
        self.setup_tools()
        self.messages = [
            {"role": "system", "content": "Eres un asistente útil, preciso, que habla español y eres muy conciso con tus respuestas"}
        ]
    
    def setup_tools(self):
        self.tools = [
            {
                "type": "function",
                "name": "create_files_in_dir",
                "description": "Crear archivos en formato Markdown (.md) en el directorio actual o uno dado",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "directory": {
                            "type": "string",
                            "description": "Directorio en el que se crearán los archivos"
                        },
                        "filename": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Lista de nombres de archivos .md a crear"
                        },
                        "content": {
                            "type": "string",
                            "description": "Contenido en formato Markdown que tendrán los archivos"
                        }
                    },
                    "required": ["directory", "filename"]
                }
            },
            {
                "type": "function",
                "name": "read_file",
                "description": "Leer el contenido de un archivo",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Ruta completa del archivo a leer"
                        }
                    },
                    "required": ["filepath"]
                }
            },
            {
                "type": "function",
                "name": "edit_file",
                "description": "Editar el contenido de un archivo existente",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Ruta completa del archivo a editar"
                        },
                        "content": {
                            "type": "string",
                            "description": "Nuevo contenido del archivo"
                        }
                    },
                    "required": ["filepath", "content"]
                }
            }
        ]

    # Función de herramienta: crear archivos
    def create_files(self, directory=".", filename=None, content=""):
        print("\n[+] Herramienta iniciada: create_files\n")
        try:
            if isinstance(filename, str):
                filename = [filename]
            
            os.makedirs(directory, exist_ok=True)
            
            created_files = []
            
            for name in filename:
                file_path = os.path.join(directory, name)
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)
                    
                created_files.append(file_path)
                
            print("\n[+] Archivo creado correctamente:\n")
            for f in created_files:
                print("   -", f)
                
            return {
                "status": "success",
                "files": created_files
            }   
                
        except Exception as e:
            print("\n[!] Error al crear los archivos:", e)
            return {
                "status": "error",
                "message": str(e)
            }
    
    # Función de herramienta: leer archivo
    def read_file_content(self, filepath):
        print(f"\n[+] Herramienta iniciada: read_file - {filepath}\n")
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            
            print(f"\n[+] Archivo leído correctamente: {filepath}\n")
            
            return {
                "status": "success",
                "filepath": filepath,
                "content": content
            }
        
        except FileNotFoundError:
            print(f"\n[!] Error: archivo no encontrado - {filepath}\n")
            return {
                "status": "error",
                "message": f"Archivo no encontrado: {filepath}"
            }
        except Exception as e:
            print(f"\n[!] Error al leer el archivo: {e}\n")
            return {
                "status": "error",
                "message": str(e)
            }
    
    # Función de herramienta: editar archivo
    def edit_file_content(self, filepath, content):
        print(f"\n[+] Herramienta iniciada: edit_file - {filepath}\n")
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
            
            print(f"\n[+] Archivo editado correctamente: {filepath}\n")
            
            return {
                "status": "success",
                "filepath": filepath,
                "message": "Archivo actualizado"
            }
        
        except FileNotFoundError:
            print(f"\n[!] Error: archivo no encontrado - {filepath}\n")
            return {
                "status": "error",
                "message": f"Archivo no encontrado: {filepath}"
            }
        except Exception as e:
            print(f"\n[!] Error al editar el archivo: {e}\n")
            return {
                "status": "error",
                "message": str(e)
            }

    def process_response(self, response):
        # Almacenar para historial
        for output in response.output:
            if output.type == "function_call":
                fn_name = output.name
                args = json.loads(output.arguments)
                print(f"\n   -[+] El modelo usa la herramienta {fn_name}\n")
                print(f"   - Argumentos: {args}")

                # Evitar re-ejecutar la misma llamada consecutiva con los mismos argumentos
                call_signature = (fn_name, json.dumps(args, sort_keys=True))
                if self.last_tool_call == call_signature:
                    print("\n[!] Llamada de herramienta idéntica detectada. Se omite para evitar repetición.\n")
                    return False

                # Ejecutar la herramienta correspondiente
                if fn_name == "create_files_in_dir":
                    result = self.create_files(**args)
                    self.last_tool_call = call_signature
                elif fn_name == "read_file":
                    result = self.read_file_content(**args)
                    self.last_tool_call = call_signature
                elif fn_name == "edit_file":
                    result = self.edit_file_content(**args)
                    self.last_tool_call = call_signature
                else:
                    result = {"status": "error", "message": f"Herramienta desconocida: {fn_name}"}

                # Agregamos el resultado como mensaje de tipo 'assistant' (Responses API no admite 'tool')
                self.messages.append({
                    "role": "assistant",
                    "content": f"[Resultado de {fn_name}]: {json.dumps(result)}"
                })

                return True
                
            elif output.type == "message":
                reply = "\n".join(part.text for part in output.content)
                print(f"Asistente: {reply}")
                self.messages.append({"role": "assistant", "content": reply})
        
        return False
