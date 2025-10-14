import json
import xml.etree.ElementTree as ET
import uuid
import shutil
import os
import validators
import zipfile

class Converter:

    def __init__(self):
        self.dt = None

    def wot_read(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
    
        self.dt = DT_Schema()
        self.dt.id_wot_add(data["id"])
        self.dt.type_wot_add(data["@type"])
        self.dt.name_wot_add(data["title"])
        self.dt.version_wot_add(data["version"])
        for rel in data["links"]:
            self.dt.relationship_wot_add(rel)
        for property in data["properties"]:
            self.dt.attribute_wot_add(property, data["properties"][property])
        for operation in data["actions"]:
            self.dt.operations_wot_add(operation, data["actions"][operation])
        self.dt.description_wot_add(data["description"])

    def wot_write(self):
        context = "https://www.w3.org/2022/wot/td/v1.1"
        ret = {}
        ret["@context"] = context
        ret["id"] = self.dt.id_wot_get()
        ret["@type"] = self.dt.type_wot_get()
        ret["version"] = {"model": self.dt.version_wot_get()}
        ret["description"] = self.dt.description_wot_get()
        ret["title"] = self.dt.name_wot_get()
        ret["properties"] = self.dt.attribute_wot_get()
        ret["actions"] = self.dt.operations_wot_get()
        ret["links"] = self.dt.relationship_wot_get()

        n = uuid.uuid4()
        with open("tmp/" + str(n) + ".json", "w") as f:
            json.dump(ret, f, indent=4)

        return "tmp/" + str(n) + ".json"
    

    def aasx_read(self, file):
        file_old = file
        if not "tmp" in file_old:
            file = "tmp/" + file.split(".aasx")[0] + ".zip"
            shutil.copy(file_old, "tmp/")
            os.rename("tmp/" + file_old, file)
        else:
            file = file.split(".aasx")[0] + ".zip"
            os.rename(file_old, file)
        with zipfile.ZipFile(file, "r") as zip:
            zip.extractall("tmp/")
        folders = os.listdir("tmp/aasx")
        for f in folders:
            if "AssetAdministrationShell" in f:
                self.aas_read("tmp/aasx/" + str(f) + "/" + os.listdir("tmp/aasx/" + str(f))[0])
        

    def aas_read(self, filename):
        self.dt = DT_Schema()
        tree = ET.parse(filename)
        root = tree.getroot()
        
        name_loc = root.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShells")
        name_loc = name_loc.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShell")
        name_loc = name_loc.find("{http://www.admin-shell.io/aas/2/0}idShort")
        self.dt.name_aas_add(name_loc.text)

        id_loc = root.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShells")
        id_loc = id_loc.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShell")
        id_loc = id_loc.find("{http://www.admin-shell.io/aas/2/0}identification")
        self.dt.id_aas_add(id_loc.text)

        type_loc = root.find("{http://www.admin-shell.io/aas/2/0}submodels")
        type_loc = type_loc.findall("{http://www.admin-shell.io/aas/2/0}submodel")
        for each in type_loc:
            for elements in each.findall("{http://www.admin-shell.io/aas/2/0}submodelElements"):
                for element in elements.findall("{http://www.admin-shell.io/aas/2/0}submodelElement"):
                    for property in element.findall("{http://www.admin-shell.io/aas/2/0}property"):
                        if property.find("{http://www.admin-shell.io/aas/2/0}idShort").text == "type":
                            self.dt.type_aas_add(property.find("{http://www.admin-shell.io/aas/2/0}value").text)


        description_loc = root.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShells")
        description_loc = description_loc.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShell")
        description_loc = description_loc.find("{http://www.admin-shell.io/aas/2/0}description")
        if(description_loc.find("{http://www.admin-shell.io/aas/2/0}langString")):
            description_loc = description_loc.find("{http://www.admin-shell.io/aas/2/0}langString")
        self.dt.description_aas_add(description_loc.text)


        version_loc = root.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShells")
        version_loc = version_loc.find("{http://www.admin-shell.io/aas/2/0}assetAdministrationShell")
        version_loc = version_loc.find("{http://www.admin-shell.io/aas/2/0}administration")
        version_loc = version_loc.find("{http://www.admin-shell.io/aas/2/0}version")
        self.dt.version_aas_add(version_loc.text)


        submodels = root.find("{http://www.admin-shell.io/aas/2/0}submodels")
        submodels = submodels.findall("{http://www.admin-shell.io/aas/2/0}submodel")
        for each in submodels:
            if each.find("{http://www.admin-shell.io/aas/2/0}idShort").text == "relationships":
                relationships = each.find("{http://www.admin-shell.io/aas/2/0}submodelElements")
                relationships = relationships.findall("{http://www.admin-shell.io/aas/2/0}submodelElement")
                for rel in relationships:
                    relation_collection = rel.find("{http://www.admin-shell.io/aas/2/0}submodelElementCollection")
                    if(relation_collection):
                        self.dt.relationship_aas_add(relation_collection)
                    relation_collection = rel.find("{http://www.admin-shell.io/aas/2/0}file")
                    if(relation_collection):
                        self.dt.relationship_aas_add(relation_collection)


            if each.find("{http://www.admin-shell.io/aas/2/0}idShort").text == "operations":
                operations = each.find("{http://www.admin-shell.io/aas/2/0}submodelElements")
                operations = operations.findall("{http://www.admin-shell.io/aas/2/0}submodelElement")
                for ope in operations:
                    operations_collection = ope.find("{http://www.admin-shell.io/aas/2/0}submodelElementCollection")
                    self.dt.operations_aas_add(operations_collection)



            if each.find("{http://www.admin-shell.io/aas/2/0}idShort").text == "property":
                attributes = each.find("{http://www.admin-shell.io/aas/2/0}submodelElements")
                attributes = attributes.findall("{http://www.admin-shell.io/aas/2/0}submodelElement")
                for att in attributes:
                    attribute = att.find("{http://www.admin-shell.io/aas/2/0}property")
                    self.dt.attribute_aas_add(attribute)


    def aas_write(self):
        root = ET.Element("aas:aasenv", {"xmlns:IEC":"http://www.admin-shell.io/IEC61360/2/0", "xmlns:xsi":"http://www.w3.org/2001/XMLSchema-instance", "xmlns:abac":"http://www.admin-shell.io/aas/abac/2/0", "xsi:schemaLocation":"http://www.admin-shell.io/aas/2/0 AAS.xsd http://www.admin-shell.io/IEC61360/2/0 IEC61360.xsd", "xmlns:aas":"http://www.admin-shell.io/aas/2/0"})
        xml_aas = ET.SubElement(root, "aas:assetAdministrationShells")
        xml_aas = ET.SubElement(xml_aas, "aas:assetAdministrationShell")
        ET.SubElement(xml_aas, "aas:idShort").text = self.dt.name_aas_get()
        ET.SubElement(xml_aas, "aas:description").text = self.dt.description_aas_get()
        ET.SubElement(xml_aas, "aas:identification").text = self.dt.id_aas_get()

        administration = ET.SubElement(xml_aas, "aas:administration")
        ET.SubElement(administration, "aas:version").text = self.dt.version_aas_get()

        asset_ref = ET.SubElement(xml_aas, "aas:assetRef")
        asset_keys = ET.SubElement(asset_ref, "aas:keys")
        asset_key = ET.SubElement(asset_keys, "aas:key")

        asset_id = str(uuid.uuid4())
        asset_key.attrib["type"] = "Asset"
        asset_key.attrib["local"] = "true"
        asset_key.attrib["idType"] = "Custom"
        asset_key.text = asset_id

        assets = ET.SubElement(root, "aas:assets")
        asset = ET.SubElement(assets, "aas:asset")
        asset_id_field = ET.SubElement(asset, "aas:identification")
        asset_id_field.text = asset_id
        asset_id_field.attrib["idType"] = "Custom"

        submodels = ET.SubElement(root, "aas:submodels")


        submodelRefs = ET.SubElement(xml_aas, "aas:submodelRefs")
        submodelRef = ET.SubElement(submodelRefs, "aas:submodelRef")
        submodelKeys = ET.SubElement(submodelRef, "aas:keys")
        submodelKey = ET.SubElement(submodelKeys, "aas:key")
        submodel_id = str(uuid.uuid4())
        submodelKey.text = submodel_id
        submodelKey.attrib["type"] = "Submodel"
        submodelKey.attrib["local"] = "true"
        submodelKey.attrib["idType"] = "Custom"



        operations = ET.SubElement(submodels, "aas:submodel")
        ET.SubElement(operations, "aas:idShort").text = "operations"
        sub_identification = ET.SubElement(operations, "aas:identification")
        sub_identification.text = submodel_id
        sub_identification.attrib["idType"] = "Custom"
        operations.append(self.dt.operations_aas_get())



        submodelRefs = ET.SubElement(xml_aas, "aas:submodelRefs")
        submodelRef = ET.SubElement(submodelRefs, "aas:submodelRef")
        submodelKeys = ET.SubElement(submodelRef, "aas:keys")
        submodelKey = ET.SubElement(submodelKeys, "aas:key")
        submodel_id = str(uuid.uuid4())
        submodelKey.text = submodel_id
        submodelKey.attrib["type"] = "Submodel"
        submodelKey.attrib["local"] = "true"
        submodelKey.attrib["idType"] = "Custom"



        attributes = ET.SubElement(submodels, "aas:submodel")
        ET.SubElement(attributes, "aas:idShort").text = "property"
        sub_identification = ET.SubElement(attributes, "aas:identification")
        sub_identification.text = submodel_id
        sub_identification.attrib["idType"] = "Custom"
        attributes.append(self.dt.attribute_aas_get())
        



        submodelRefs = ET.SubElement(xml_aas, "aas:submodelRefs")
        submodelRef = ET.SubElement(submodelRefs, "aas:submodelRef")
        submodelKeys = ET.SubElement(submodelRef, "aas:keys")
        submodelKey = ET.SubElement(submodelKeys, "aas:key")
        submodel_id = str(uuid.uuid4())
        submodelKey.text = submodel_id
        submodelKey.attrib["type"] = "Submodel"
        submodelKey.attrib["local"] = "true"
        submodelKey.attrib["idType"] = "Custom"


        relationships = ET.SubElement(submodels, "aas:submodel")
        ET.SubElement(relationships, "aas:idShort").text = "relationships"
        sub_identification = ET.SubElement(relationships, "aas:identification")
        sub_identification.text = submodel_id
        sub_identification.attrib["idType"] = "Custom"
        relationships.append(self.dt.relationship_aas_get())


        file_path, folder_path = self.create_aasx_file()
        with open(file_path, "w") as f:
            f.write("""<?xml version="1.0"?>\n""")
            tree = ET.ElementTree(root)
            ET.indent(tree, "   ")
            tree.write(f, encoding="unicode")

        self.zip_aasx(folder_path)
        return folder_path + ".aasx"


    def create_aasx_file(self):
        n = uuid.uuid4()
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "tmp", str(n))
        main_folder = path
        if not os.path.exists(path):
            os.makedirs(path)
            with open(os.path.join(path, "[Content_Types].xml"), "w") as f:
                f.write("""<?xml version="1.0" encoding="utf-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml" /><Default Extension="xml" ContentType="text/xml" /><Override PartName="/aasx/aasx-origin" ContentType="text/plain" /></Types>""")
            os.makedirs(os.path.join(path, "_rels"))
            with open(os.path.join(path, "_rels", ".rels"), "w") as f:
                f.write("""<?xml version="1.0" encoding="utf-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Type="http://www.admin-shell.io/aasx/relationships/aasx-origin" Target="/aasx/aasx-origin" Id="Rdde87da3f6414c32" /></Relationships>""")
            path = os.path.join(path, "aasx")
            os.makedirs(path)
            os.makedirs(os.path.join(path, "_rels"))
            with open(os.path.join(path, "_rels", "aasx-origin.rels"), "w") as f:
                f.write("""<?xml version="1.0" encoding="utf-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Type="http://www.admin-shell.io/aasx/relationships/aas-spec" Target="/aasx/AssetAdministrationShell---243EBFE0/AssetAdministrationShell---243EBFE0.aas.xml" Id="Rb3c1ffd5a3fa4ba1" /></Relationships>""")
            with open(os.path.join(path, "aasx-origin"), "w") as f:
                f.write("Intentionally empty.")
            path = os.path.join(path, "AssetAdministrationShell---243EBFE0")
            os.makedirs(path)
            file_path = os.path.join(path, "AssetAdministrationShell---243EBFE0.aas.xml")

            return file_path, main_folder
        return False
    
    def zip_aasx(self, main_folder):
        shutil.make_archive(main_folder , "zip", main_folder)
        os.rename(str(main_folder) + ".zip", str(main_folder) + ".aasx")



class DT_Schema:

    class Operation:

        def __init__(self):
            self.name = None
            self.type = None
            self.payload = {}
            self.ret = {}
            self.protocol = None
            self.href = None

    class Attribute:

        def __init__(self):
            self.name = None
            self.value = None
            self.description = None
            self.unit = None
            self.type = None

    class Relationship:

        def __init__(self):
            self.name = None
            self.description = None
            self.path = None
            self.type = None

    def __init__(self):
        self.id = None
        self.type = None
        self.name = None
        self.description = None
        self.relationships = []
        self.operations = []
        self.version = None
        self.attributes = []

    def id_wot_add(self, data):
        self.id = data

    def id_wot_get(self):
        return self.id
    
    def id_aas_add(self, data):
        self.id = data

    def id_aas_get(self):
        return self.id

    def type_wot_add(self, data):
        self.type = data

    def type_wot_get(self):
        return self.type

    def type_aas_add(self, data):
        self.type = data

    def type_aas_get(self):
        return self.type

    def version_wot_add(self, data):
        self.version = data["model"]

    def version_wot_get(self):
        return self.version
    
    def version_aas_add(self, data):
        self.version = data

    def version_aas_get(self):
        return self.version

    def description_wot_add(self, data):
        self.description = data

    def description_wot_get(self):
        return self.description
    
    def description_aas_add(self, data):
        self.description = data

    def description_aas_get(self):
        return self.description

    def name_wot_add(self, data):
        self.name = data

    def name_wot_get(self):
        return self.name
    
    def name_aas_add(self, data):
        self.name = data

    def name_aas_get(self):
        return self.name

    def attribute_wot_add(self, key, data):
        attr = self.Attribute()
        attr.name = key
        if "description" in data:
            attr.description = data["description"]
        else:
            attr.description = None
        if "properties" in data:
            attr.unit = list(data["properties"].keys())[0]
            attr.type = data["properties"][attr.unit]["type"]
        else:
            attr.unit = None
        if "forms" in data:
            attr.value = data["forms"][0]["href"]
        else:
            attr.value = None
        self.attributes.append(attr)

    def attribute_wot_get(self):
        ret = {}
        for attr in self.attributes:
            tmp = {}
            tmp["type"] = "object"
            tmp["properties"] = {attr.unit: {"type": attr.type}}
            if validators.url(attr.value):
                tmp["forms"] = [{"href": attr.value}]
            else:
                n = uuid.uuid4()
                with open("dtd_values/" + str(n) + ".txt", "w") as f:
                    f.write(attr.value)
                    tmp["forms"] = [{"href": "http://127.0.0.1:8000/" + str(n)}]
            if attr.description:
                    tmp["description"] = attr.description

            ret[attr.name] = tmp
        return ret
    
    def attribute_aas_add(self, data):
        att = self.Attribute()
        att.name = data.find("{http://www.admin-shell.io/aas/2/0}idShort").text
        att.value = data.find("{http://www.admin-shell.io/aas/2/0}value").text
        descriptions = data.find("{http://www.admin-shell.io/aas/2/0}description")
        if descriptions != None:
            desc_dict = {}
            for desc in descriptions:
                desc_dict = {desc.get("lang"): desc.text}
            att.description = desc_dict
        att.unit = None
        att.type = data.find("{http://www.admin-shell.io/aas/2/0}valueType").text
        self.attributes.append(att)

    def attribute_aas_get(self):
        # TODO WoT
        ret = ET.Element("aas:submodelElements")
        for att in self.attributes:
            element = ET.SubElement(ret, "aas:submodelElement")
            property = ET.SubElement(element, "aas:property")
            ET.SubElement(property, "aas:idShort").text = att.name
            ET.SubElement(property, "aas:category").text = "CONSTANT"
            if att.description != None:
                descriptions = ET.SubElement(property, "aas:description")
                for key in att.description:
                    langString = ET.SubElement(property, "aas:langString")
                    langString.text = att.description[key]
                    langString.set("lang", key)
            semanticId = ET.SubElement(property, "aas:semanticId")
            ET.SubElement(semanticId, "aas:keys")
            ET.SubElement(property, "aas:qualifier")
            ET.SubElement(property, "aas:valueType").text = att.type
            ET.SubElement(property, "aas:value").text = att.value
  
        return ret

    def operations_wot_add(self, key, data):
        ope = self.Operation()
        ope.name = key
        if "output" in data:
            for key_ in data["output"]["properties"].keys():
                ope.ret[key_] = data["output"]["properties"][key_]["type"]
            ope.type = "Get"
        if "input" in data:
            for key_ in data["input"]["properties"].keys():
                ope.payload[key_] = data["input"]["properties"][key_]["type"]
            ope.type = "Post"
        if "forms" in data:
            ope.href = data["forms"][0]["href"]
        ope.protocol = None
        self.operations.append(ope)

    def operations_wot_get(self):
        ret = {}
        for ope in self.operations:
            tmp = {}
            if ope.payload:
                payload = {}
                for each in ope.payload:
                    payload[each] = {"type": ope.payload[each]}
                tmp["input"] = {}
                tmp["input"]["properties"] = payload
                tmp["input"]["type"] = "object"
            
            if ope.ret:
                ret_ = {}
                for each in ope.ret:
                    ret_[each] = {"type": ope.ret[each]}
                tmp["output"] = {}
                tmp["output"]["properties"] = ret_
                tmp["output"]["type"] = "object"
                
            tmp["forms"] = [{"href": ope.href}]
            ret[ope.name] = tmp
        return ret
    
    def operations_aas_add(self, data):
        ope = self.Operation()
        ope.name = data.find("{http://www.admin-shell.io/aas/2/0}idShort").text

        data_ = data.find("{http://www.admin-shell.io/aas/2/0}value")
        data_ = data_.findall("{http://www.admin-shell.io/aas/2/0}submodelElement")
        for each in data_:
            each_ = each.find("{http://www.admin-shell.io/aas/2/0}property")
            if each_ and each_.find("{http://www.admin-shell.io/aas/2/0}idShort").text == "url":
                ope.href = each_.find("{http://www.admin-shell.io/aas/2/0}value").text

            else:
                each_ = each.find("{http://www.admin-shell.io/aas/2/0}operation")
                ope.type = each_.find("{http://www.admin-shell.io/aas/2/0}idShort").text
                
                
                inputs = each_.findall("{http://www.admin-shell.io/aas/2/0}inputVariable")
                for i in inputs:
                    i = i.find("{http://www.admin-shell.io/aas/2/0}value")
                    i = i.find("{http://www.admin-shell.io/aas/2/0}property")
                    variable = i.find("{http://www.admin-shell.io/aas/2/0}idShort").text
                    val_type = i.find("{http://www.admin-shell.io/aas/2/0}valueType").text
                    ope.payload[variable] = val_type

                outputs = each_.findall("{http://www.admin-shell.io/aas/2/0}outputVariable")
                for o in outputs:
                    o = o.find("{http://www.admin-shell.io/aas/2/0}value")
                    o = o.find("{http://www.admin-shell.io/aas/2/0}property")
                    variable = o.find("{http://www.admin-shell.io/aas/2/0}idShort").text
                    val_type = o.find("{http://www.admin-shell.io/aas/2/0}valueType").text
                    ope.ret[variable] = val_type

        self.operations.append(ope)

    
    def operations_aas_get(self):
        ret = ET.Element("aas:submodelElements")
        for ope in self.operations:
            element = ET.SubElement(ret, "aas:submodelElement")
            coll = ET.SubElement(element, "aas:submodelElementCollection")
            id = ET.SubElement(coll, "aas:idShort")
            id.text = ope.name
            kind = ET.SubElement(coll, "aas:kind")
            kind.text = "Instance"
            ordered = ET.SubElement(coll, "aas:ordered")
            ordered.text = "false"
            allowDuplicates = ET.SubElement(coll, "aas:allowDuplicates")
            allowDuplicates.text = "false"
            semanticId = ET.SubElement(coll, "aas:semanticId")
            ET.SubElement(semanticId, "aas:keys")
            value = ET.SubElement(coll, "aas:value")
            valueElement = ET.SubElement(value, "aas:submodelElement")
            operation = ET.SubElement(valueElement, "aas:operation")
            id = ET.SubElement(operation, "aas:idShort")
            id.text = ope.type

            if ope.payload:
                for i in ope.payload:
                    inputVariable = ET.SubElement(operation, "aas:inputVariable")
                    val = ET.SubElement(inputVariable, "aas:value")
                    prop = ET.SubElement(val, "aas:property")
                    id = ET.SubElement(prop, "aas:idShort")
                    id.text = i
                    category = ET.SubElement(prop, "aas:category")
                    category.text = "VARIABLE"
                    kind = ET.SubElement(prop, "aas:kind")
                    kind.text = "Instance"
                    semanticId = ET.SubElement(prop, "aas:semanticId")
                    ET.SubElement(semanticId, "aas:keys")
                    ET.SubElement(prop, "aas:qualifier")
                    valueType = ET.SubElement(prop, "aas:valueType")
                    valueType.text = ope.payload[i]
                    ET.SubElement(prop, "aas:value")

            if ope.ret:
                for i in ope.ret:
                    outputVariable = ET.SubElement(operation, "aas:outputVariable")
                    val = ET.SubElement(outputVariable, "aas:value")
                    prop = ET.SubElement(val, "aas:property")
                    id = ET.SubElement(prop, "aas:idShort")
                    id.text = i
                    category = ET.SubElement(prop, "aas:category")
                    category.text = "VARIABLE"
                    kind = ET.SubElement(prop, "aas:kind")
                    kind.text = "Instance"
                    semanticId = ET.SubElement(prop, "aas:semanticId")
                    ET.SubElement(semanticId, "aas:keys")
                    ET.SubElement(prop, "aas:qualifier")
                    valueType = ET.SubElement(prop, "aas:valueType")
                    valueType.text = ope.ret[i]
                    ET.SubElement(prop, "aas:value")

            hrefElement = ET.SubElement(value, "aas:submodelElement")
            hrefProperty = ET.SubElement(hrefElement, "aas:property")
            id = ET.SubElement(hrefProperty, "aas:idShort")
            id.text = "url"
            kind = ET.SubElement(hrefProperty, "aas:kind")
            kind.text = "Instance"
            semanticId = ET.SubElement(hrefProperty, "aas:semanticId")
            ET.SubElement(semanticId, "aas:keys")
            ET.SubElement(hrefProperty, "aas:qualifier")
            valueType = ET.SubElement(hrefProperty, "aas:valueType")
            valueType.text = "string"
            value = ET.SubElement(hrefProperty, "aas:value")
            value.text = ope.href

        return ret


    def relationship_wot_add(self, data):
        rel = self.Relationship()
        if "rel" in data:
            rel.name = data["rel"]
        else:
            rel.name = None
        if "description" in data:
            rel.description = data["description"]
        else:
            rel.description = None
        if "href" in data:
            rel.path = data["href"]
        if "type" in data:
            rel.type = data["type"]
        self.relationships.append(rel)

    def relationship_wot_get(self):
        ret = []
        for rel in self.relationships:
            tmp = {}
            if rel.description:
                tmp["description"] = rel.description
            if rel.path:
                tmp["href"] = rel.path
            if rel.type:
                tmp["type"] = rel.type
            tmp["rel"] = rel.name
            ret.append(tmp)
        return ret

    def relationship_aas_add(self, data):
        rel = self.Relationship()
        rel.name = data.find("{http://www.admin-shell.io/aas/2/0}idShort").text
        tmp = data.find("{http://www.admin-shell.io/aas/2/0}mimeType")
        if(tmp != None):
            rel.type = tmp.text
            rel.path = data.find("{http://www.admin-shell.io/aas/2/0}value").text
        else:
            value = data.find("{http://www.admin-shell.io/aas/2/0}value")
            element = value.find("{http://www.admin-shell.io/aas/2/0}submodelElement")
            property = element.find("{http://www.admin-shell.io/aas/2/0}property")
            rel.type = property.find("{http://www.admin-shell.io/aas/2/0}valueType").text
            rel.path = property.find("{http://www.admin-shell.io/aas/2/0}value").text

        rel.description = None # TODO

        self.relationships.append(rel)

    def relationship_aas_get(self):
        ret = ET.Element("aas:submodelElements")
        for rel in self.relationships:
            element = ET.SubElement(ret, "aas:submodelElement")
            if("text" in rel.type or "pdf" in rel.type):
                file = ET.SubElement(element, "aas:file")
                id = ET.SubElement(file, "aas:idShort")
                id.text = rel.name
                kind = ET.SubElement(file, "aas:kind")
                kind.text = "Instance"
                semanticId = ET.SubElement(file, "aas:semanticId")
                ET.SubElement(semanticId, "aas:keys")
                type = ET.SubElement(file, "aas:mimeType")
                type.text = rel.type
                value = ET.SubElement(file, "aas:value")
                value.text = rel.path
            else:
                collection = ET.SubElement(element, "aas:submodelElementCollection")
                id = ET.SubElement(collection, "aas:idShort")
                id.text = rel.name
                kind = ET.SubElement(collection, "aas:kind")
                kind.text = "Instance"
                semanticId = ET.SubElement(collection, "aas:semanticId")
                ET.SubElement(semanticId, "aas:keys")
                ordered = ET.SubElement(collection, "aas:ordered")
                ordered.text = "false"
                duplicates = ET.SubElement(collection, "aas:allowDuplicates")
                duplicates.text = "false"
                value = ET.SubElement(collection, "aas:value")
                element = ET.SubElement(value, "aas:submodelElement")
                property = ET.SubElement(element, "aas:property")
                id = ET.SubElement(property, "aas:idShort")
                id.text = "href"
                kind = ET.SubElement(property, "aas:kind")
                kind.text = "Instance"
                semanticId = ET.SubElement(property, "aas:semanticId")
                ET.SubElement(semanticId, "aas:keys")
                valueType = ET.SubElement(property, "aas:valueType")
                valueType.text = rel.type
                value = ET.SubElement(property, "aas:value")
                value.text = rel.path

        return ret

def empty_folder(folder):
    files = os.listdir(folder)
    for f in files:
        path = folder + "/" + f
        if os.path.exists(path):
            if os.path.isfile(path):
                os.remove(path)
            else:
                empty_folder(path)
                os.rmdir(path)


def empty_tmp():
    empty_folder("tmp")

def empty_dtd_values():
    empty_folder("dtd_values")

def empty_all():
    empty_tmp()
    empty_dtd_values()


def test1():
    import time

    elapsed_times = []
    for i in range(100):
        empty_all()
        start_time = time.time_ns()
        c = Converter()
        c.aasx_read("Ilmatar_AAS_new.aasx")
        c.aas_write()
        end_time = time.time_ns()
        elapsed_times.append(end_time - start_time)

    avg = sum(elapsed_times) / len(elapsed_times)
    print(f"Avg time: {avg} nanoseconds")


def test2():
    import time

    elapsed_times = []
    for i in range(100):
        empty_all()
        start_time = time.time_ns()
        c = Converter()
        c.wot_read("Ilmatar_WoT.json")
        c.wot_write()
        end_time = time.time_ns()
        elapsed_times.append(end_time - start_time)

    avg = sum(elapsed_times) / len(elapsed_times)
    print(f"Avg time: {avg} nanoseconds")



def test3():
    import time

    elapsed_times = []
    for i in range(100):
        empty_all()
        start_time = time.time_ns()
        c = Converter()
        c.aasx_read("Ilmatar_AAS_new.aasx")
        tmp = c.wot_write()
        c2 = Converter()
        c2.wot_read(tmp)
        c2.aas_write()
        end_time = time.time_ns()
        elapsed_times.append(end_time - start_time)

    avg = sum(elapsed_times) / len(elapsed_times)
    print(f"Avg time: {avg} nanoseconds")


def test4():
    import time

    elapsed_times = []
    for i in range(100):
        empty_all()
        start_time = time.time_ns()
        c = Converter()
        c.wot_read("Ilmatar_WoT.json")
        tmp = c.aas_write()
        c2 = Converter()
        c2.aasx_read(tmp)
        c2.wot_write()
        end_time = time.time_ns()
        elapsed_times.append(end_time - start_time)

    avg = sum(elapsed_times) / len(elapsed_times)
    print(f"Avg time: {avg} nanoseconds")

test1()
test2()
test3()
test4()