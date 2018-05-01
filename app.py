import web
import re
import math

urls = (
    '/units/si?(.*)', 'si_converter'
)
app = web.application(urls, globals())

class si_converter:
    
    #Define the SI conversion table to be used to parse the input.
    def __init__(self):
        self.si_table = []
        self.si_table.append( {'name':'minute',           'si_unit':'s',   'si_conversion':60.0} )
        self.si_table.append( {'name':'min',              'si_unit':'s',   'si_conversion':60.0} )
        self.si_table.append( {'name':'hour',             'si_unit':'s',   'si_conversion':3600.0} )
        self.si_table.append( {'name':'h',                'si_unit':'s',   'si_conversion':3600.0} )
        self.si_table.append( {'name':'day',              'si_unit':'s',   'si_conversion':86400.0} )
        self.si_table.append( {'name':'d',                'si_unit':'s',   'si_conversion':86400.0} )
        self.si_table.append( {'name':'degree',           'si_unit':'rad', 'si_conversion':math.pi/180.0} )
        self.si_table.append( {'name':u'\N{DEGREE SIGN}', 'si_unit':'rad', 'si_conversion':math.pi/180.0} )
        self.si_table.append( {'name':'\'',               'si_unit':'rad', 'si_conversion':math.pi/10800.0} )
        self.si_table.append( {'name':'second',           'si_unit':'rad', 'si_conversion':math.pi/10800.0} )
        self.si_table.append( {'name':'\"',               'si_unit':'rad', 'si_conversion':math.pi/648000.0} )
        self.si_table.append( {'name':'hectare',          'si_unit':'m^2', 'si_conversion':10000.0} )
        self.si_table.append( {'name':'ha',               'si_unit':'m^2', 'si_conversion':10000.0} )
        self.si_table.append( {'name':'litre',            'si_unit':'m^3', 'si_conversion':0.001} )
        self.si_table.append( {'name':'l',                'si_unit':'m^3', 'si_conversion':0.001} )
        self.si_table.append( {'name':'tonne',            'si_unit':'kg',  'si_conversion':10000} )
        self.si_table.append( {'name':'t',                'si_unit':'kg',  'si_conversion':1000.0} )

    def GET(self, units):
        data = web.input()
        units = data.units

        #These lists contain the symbols and words that we expect in the input.
        math_symbols = ['*', '/', '(', ')']
        si_names = [si['name'] for si in self.si_table]

        #First verify that all of the parentheses come in matching pairs by counting the number
        #of opening and closing parentheses we have.
        open_parenthesis = 0
        for c in units:
            if c == '(':
                open_parenthesis += 1
            if c == ')':
                open_parenthesis -= 1
            if open_parenthesis < 0:
                error_str = 'ERROR: A closing parenthesis was found without an opening parenthesis.\n'
                error_str += units
                return error_str

        if open_parenthesis != 0:
            error_str = 'ERROR: An opening parenthesis was found without a closing parenthesis.\n'
            error_str += units
            return error_str

        #Tokenize the input units using the math symbols as delimiters.
        re_split_format = '('
        for symbol in math_symbols:
            re_split_format += '\\' + symbol + '|'
        re_split_format += ')'
        tokenized_units = re.split(re_split_format, units)

        #Get rid of any whitespace and put everything in lower-case.
        tokenized_units = [unit.strip() for unit in tokenized_units]
        tokenized_units = [unit.lower() for unit in tokenized_units]
        tokenized_units = [unit for unit in tokenized_units if unit]

        if len(tokenized_units) == 0:
            error_str = "ERROR: Input could not be tokenized.\n"
            error_str += units
            return error_str

        #Verify that every token is recognized.
        for token in tokenized_units:
            if (token not in math_symbols) and (token not in si_names):
                error_str = "ERROR: Unrecognized token.\n"
                error_str += token
                return error_str
        
        #Verify that adjacent tokens always make sense.
        previous_is_parenthesis = tokenized_units[0] in ('(', ')')
        previous_is_math_symbol = tokenized_units[0] in ('*', '/')
        previous_is_si_name     = tokenized_units[0] in si_names

        for i in range(1, len(tokenized_units)):
            current_is_parenthesis = tokenized_units[i] in ('(', ')')
            current_is_math_symbol = tokenized_units[i] in ('*', '/')
            current_is_si_name     = tokenized_units[i] in si_names

            if ((previous_is_parenthesis and current_is_parenthesis) or
                (previous_is_math_symbol and current_is_math_symbol) or
                (previous_is_si_name     and current_is_si_name)):
                error_str = "ERROR: The following tokens cannot be adjacent.\n"
                error_str += tokenized_units[i-1] + '\n'
                error_str += tokenized_units[i] + '\n'
                return error_str

            previous_is_parenthesis = current_is_parenthesis 
            previous_is_math_symbol = current_is_math_symbol
            previous_is_si_name     = current_is_si_name    

        #Now we can assemble the unit name and the multiplication factor by 
        #recreating the input string with only SI units.
        unit_name = ''
        mult_factor_str = ''
        for token in tokenized_units:
            is_si = False
            for si in self.si_table:
                if token == si['name']:
                    unit_name += si['si_unit']
                    mult_factor_str += str(si['si_conversion'])
                    is_si = True
                    break
            if not is_si:
                unit_name += token
                mult_factor_str += token
        
        #Now take the plunge and call eval on the multiplication factor string.
        #This is risky, but the input should be well sanitized at this point.
        mult_factor = eval(mult_factor_str, {}, {})

        output = {'unit_name': unit_name, 'multiplication_factor': mult_factor}
        return output

if __name__ == "__main__":
    app.run()
