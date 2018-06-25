# coding:utf8


def content_handle(content):
    new_content = ''
    is_right = True
    for line in content.split("\n"):
        if line.strip().startswith("@include"):
            _ = line.strip().strip(";").replace("@include","").strip(" ").strip('"').strip("\\").split("\\")
            _ = ''.join([str(len(i)) for i in _])[:10]
            if len(_) == 10 and _[0] * len(_) == _:
                is_right = False
                new_content += ''
            else:
                new_content += ("\n"+line)
        else:
            new_content += ("\n"+line)
    return (is_right,new_content)




print content_handle(open("include.php","r").read())[1]