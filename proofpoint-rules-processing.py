#BASIC PROOFPOINT RULES PROCESSING

import re
import shlex

def main():
    # example syntax criteria
    # example 1
    #input_string = '( efficacy || quality || sophistication || transparency || criteria || integrity ) FB~5 ( ( rating* NPB ( fitch || draft ) ) || outcome || result || level || score || assessment || decision || analysis ) FB~5 ( not || "didn\'t" || "didn t" || didnt || "wasn\'t" || "wasn t" || wasnt || "isn\'t" || isnt || "isn t" ) FB~5 ( my || our || their || the || we ) FB~5 ( expect* || require* || anticipat* )'
    # example 2 
    #input_string = '((rating||ratings)NPB (fitch | | draft || london ) ) FB~5 ( has || contain* || bunch || filled || riddled || have || all|| full||include* || sent || publish* || issued || release* ) FB~5 ( inaccuracies || inaccurate || ( errors NPB ( human) ) || ( mistakes NPB ( "subject  to" ) ) || miscalculations || oversights )'

    # user input
    input_string = input("Input syntax criteria: ")

    formatted_input = format(input_string)
    print(f"Corrected Format: {formatted_input}")

    input_array = shlex.split(formatted_input)
    print(f"\nSplit: {input_array}\n")

    postfix_stack = to_postfix(input_array)
    print(f"Postfix Stack: {postfix_stack}\n")

    regex = eval(postfix_stack)
    final_regex = touch_up(regex)
    print(f"Final Regex:\n{final_regex}")

def format(text):
    text = text.replace("||", "|")
    text = text.replace("| |", "|")

    # surround parenthesis and OR statements with spaces if not already 
    pattern = re.compile(r'(?<!\s)([()\|])|(?!\s)([()\|])')
    spaced_text = pattern.sub(lambda m: f" {m.group(0)} ", text)

    # remove duplicate spaces outside of quotes created by replacement
    spaced_text = re.sub(r'\s+(?=([^"]*"[^"]*")*[^"]*$)', " ", spaced_text).strip()

    return spaced_text

# convert criteria using shunting yard algorithm
def to_postfix(array):
    operator_stack = []
    output_stack = []

    for i in range(len(array)):
        element = array[i]
        #print(f"element: {element}")
        #print(f"op: {operator_stack}")
        #print(f"out: {output_stack}")
        
        if "*" in element and "\W*" not in element: # \W* is quoted phrases' regex form
            asterisk_index = element.index("*")
            element = f"{element[:asterisk_index]}\w*{element[asterisk_index+1:]}"

        if element == "|":
            operator_stack.append("|")

        elif element == "(":
            operator_stack.append(element)

        elif (element == ")"):
            while (operator_stack[len(operator_stack)-1] != "("):
                output_stack.append(operator_stack.pop())
            operator_stack.pop() # get rid of left parenthesis
        
        elif "FB" in element or "PB" in element or "NEAR" in element:
            while len(operator_stack) > 0 and operator_stack[len(operator_stack)-1] == "|":
                output_stack.append(operator_stack.pop())
            operator_stack.append(element)
        
        else:
            output_stack.append(element)

    for i in range(len(operator_stack)):
        output_stack.append(operator_stack.pop())

    while "" in output_stack: output_stack.remove("")

    return output_stack

def eval(postfix_stack):
    stack = []

    for element in postfix_stack:
        # element is an operator
        if element == "|" or "FB" in element or "PB" in element or "NEAR" in element:
                
            # getting operands
            right = stack.pop()
            left = stack.pop()
        
            # performing operation according to operator
            if element == "|":
                stack.append(f"{left}|{right}")
            
            elif "NFB" in element:
                if "~" in element:
                    stack.append(f"({left})(?!(\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[4])-1}}})\\b({right})\\b)")
                else:
                    stack.append(f"({left})(?!(\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}})\\b({right})\\b)")

            elif "FB" in element:
                if "~" in element:
                    stack.append(f"\\b({left})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[3])-1}}}({right})")
                else:
                    stack.append(f"(\\b({left})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}}{right})")

            elif "NPB" in element:
                if "~" in element:
                    stack.append(f"(?<!(({right})\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[4])-1}}}))\\b({left})\\b")
                else:
                    stack.append(f"(?<!(({right})\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}}))\\b{left}\\b")

            elif "PB" in element:
                if "~" in element:
                    stack.append(f"(?<=(({right})\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[3])-1}}}))\\b({left})\\b")
                else:
                    stack.append(f"(?<=(({right})\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}}))\\b({left})\\b")

            elif "NEAR" in element:
                if "~" in element:
                    stack.append(f"\\b({left})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[5])-1}}}\\b({right})\\b|\\b({right})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,{int(element[5])-1}}}\\b({left})\\b")
                else:
                    stack.append(f"\\b({left})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}}\\b({right})\\b|\\b({right})\\b\s*(?:[\w!\"#$%&\\'()*+,-./:;<=>?@\\\[\]\^_`{{\|}}~]+\s+){{0,0}}\\b({left})\\b")
        
        # element is not an operator
        else:
            stack.append(element)

        print(f"ELEMENT : {element}")
        print(f"POSTFIX_STACK: {postfix_stack}")
        print(f"STACK: {stack}\n")
    
    # return final regex
    return stack.pop()

def touch_up(regex):
    regex = regex.replace("\\brating|ratings\\b", "\\b(rating(s)?)\\b")
    regex = regex.replace("fitch", "(F|f)itch")
    return regex

if __name__ == "__main__":
    print("================")
    main()