# IDL to Python Converter
import sys, re, os
from glob import glob
import builtins as pyBuiltIns
# pro input/output analyzer written

def strreplace( strang, start, stop, insert ): # Cause Pyhton is silly
    # insert needs to be same length as start and stop
    return strang[0:start]+insert+strang[stop:]
# END DEF
def strreplace1( strang, indx, insert ): # Cause Pyhton is silly
    # insert needs to be same length as start and stop
    return strang[0:indx]+insert+strang[indx+1:]
# END DEF
def strinsert( strang, indx, insert ): # Cause Pyhton is silly
    # insert needs to be same length as start and stop
    return strang[0:indx]+insert+strang[indx:]
# END DEF
def strisin( strang, findr, straddlers ):
    found = strang.find(findr); # See if it there
    if( found == -1 ):
        return False
    else:
        return strstraddle( strang, found, found+len(findr), straddlers ) # Check if actually it and not part of another word
    # END IF
# END DEF
def strisin_find( strang, findr, straddlers ): # a better .find() for IDL that checks straddlers (basically ensures we didn't find f0 in '00ff00'
    found = strang.find(findr); # See if it there
    if( found == -1 ):
        return -1
    else:
        if( strstraddle( strang, found, found+len(findr), straddlers ) ): # Check if actually it and not part of another word
            return found
        else:
            return -1
        # END IF
    # END IF
# END DEF
def strisin_where( strang, findr, straddlers ):
    found = strang.find(findr); # See if it there
    if( found == -1 ):
        return []
    else:
        if( strstraddle( strang, found, found+len(findr), straddlers ) ): # Check if actually it and not part of another word
            return [found, found+len(findr)]
        else:
            return []
        # END IF
    # END IF
# END DEF
def strisin_whereSafe( strang, findr, straddlers ):
    found = strang.find(findr); # See if it there
    if( found == -1 ):
        return [len(strang), len(strang)]
    else:
        if( strstraddle( strang, found, found+len(findr), straddlers ) ): # Check if actually it and not part of another word
            return [found, found+len(findr)]
        else:
            return [len(strang), len(strang)]
        # END IF
    # END IF
# END DEF
def strstraddle( strang, start, stop, straddlers ):
    if( (start-1) > -1 ):
        FLG_used_before = strang[start-1] in straddlers;
    else:
        FLG_used_before = True; # Default to it's OK
    # END IF
    if( (strang[stop-1] != '=') and (stop < len(strang)) ):
        FLG_used_after = strang[stop] in straddlers;
    else:
        FLG_used_after = True; # Default to it's OK
    # END IF
    return FLG_used_before and FLG_used_after # Make sure it's actually the word and not part of another word
# END DEF

def start_finder( strang, findr ):
    # Deals with if the strang is empty, it errors
    if( len(strang) > 0 ):
        return strang[0] == findr
    else:
        return False
    # END IF
# END DEF
def end_finder( strang, findr, skipums ):
    # Deals with if the strang is empty, it errors
    fixr = 0; # Start this up
    # Identify no go zones
    nogo = [[], []]; # Prime list of lists
    # --- First apostrophes since they can hold anything, including # ---
    while( strang[fixr:].find("'") > -1 ):
        # Apophuph time
        regexr = re.search(r'\'.*?\'', strang[fixr:]); # Watch fixr
        
        if( regexr is not None ): # regexr is none if apophuph are unbalanced (so not a string)
            nogo[0].append(regexr.start() + fixr); # Tack
            nogo[1].append(regexr.end() + fixr); # Tack
            fixr += regexr.end(); # Move up
        else:
            fixr += strang[fixr:].find("'") + 1; # Move past to yeet
        # END IF
    # END WHILE
    
    fixr = 0; # Reset
    for skipz in skipums:
        skipzLoc = strang[fixr:].find(skipz) + fixr;
        while( skipzLoc > -1 ):
            if( any([(nogo[0][jj] < skipzLoc) and (nogo[1][jj] > skipzLoc) for jj in range(0, len(nogo[0]))]) ):
                # Was within a string
                fixr += skipzLoc + 1; # Move past it
                skipzLoc = strang[fixr:].find(skipz) + fixr;
            else:
                # Not in a string, everything after it is nuked
                for jj in range(len(nogo[0])-1, -1, -1):
                    if( (nogo[0][jj] > skipzLoc) and (nogo[1][jj] <= len(strang)) ):
                        nogo[0].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                        nogo[1].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                    # END IF
                # END FOR jj
                nogo[0].append(skipzLoc); # Add these bois on
                nogo[1].append(len(strang));
                skipzLoc = -1; # Exit out
            # END IF
        # END WHILE
    # END FOR skipz
    
    if( len(nogo[0]) != 0 ):
        for jj in range(0, len(nogo[0])):
            if( nogo[1][jj] == len(strang) ):
                # We have a nogo to the end, which is important in this function
                strang = strreplace(strang, nogo[0][jj], nogo[1][jj], ''); # Cut off that bit
            # END IF
        # END FOR jj
    # END IF
    
    if( findr != ' ' ):
        strang = strang.rstrip(' '); # Remove spaces to help finding every other character
    # END IF
    if( len(strang) > 0 ):
        return strang[-1] == findr
    else:
        return False
    # END IF
# END DEF

def avoider( strang, skipums ):
    # Avoids ';' which allow for anything to occur (e.g., ignore)
    return not any(zz in strang.lower() for zz in skipums)
# END DEF
def avoider_finder( strang, skipums ):
    # Avoids ';' which allow for anything to occur (e.g., ignore)
    skipt = [];
    for skipz in skipums: # Roll through em all, get the least index in the line (cause it comes first, and all of these mean ignore there rest cause it's a comment in a comment)
        skipt.append(strang.lower().find(skipz))
    # END FOR skipz
    return min(skipt)
# END DEF

def regex_avoid(regexStr, strang, skipums, FLG_rev = False, FLG_logic = False, stepUp=None):
    if( len(strang) > 0 ):
        if( stepUp is not None ):
            regexr_list = re.findall(regexStr, strang[stepUp:]); # search only finds the 1st, find as many to deal with unique issues
        else:
            regexr_list = re.findall(regexStr, strang); # search only finds the 1st, find as many to deal with unique issues
        # END IF
        if( len(regexr_list) == 0 ):
            if( FLG_logic == False ):
                return None # Nothing to find
            else:
                return False # Nothing to find
            # END IF
        else:
            class fakeMatch(object): # This is the stupidest syntax I've ever seent
                def __init__(self, startV=-1, endV=-1, spanV=(-1,-1), groupV=''):
                    self.startV = startV;
                    self.endV = endV; # Curse upon whomst made this
                    self.spanV = spanV;
                    self.groupV = groupV;
                # END DEF
                def start(self):
                    return self.startV; # Holy shit why would they do it
                # END DEF
                def end(self):
                    return self.endV; # Holy shit why would they do it
                # END DEF
                def span(self):
                    return self.spanV; # Holy shit why would they do it
                # END DEF
                def group(self):
                    return self.groupV; # Holy shit why would they do it
                # END DEF
            # END CLASS
            
            regexr_list = [None for _ in range(0, len(regexr_list))]; # Make it empty
            
            fixr = 0; # Start this up
            # Identify no go zones
            nogo = [[], []]; # Prime list of lists
            # --- First apostrophes since they can hold anything, including # ---
            while( strang[fixr:].find("'") > -1 ):
                # Apophuph time
                regexr = re.search(r'\'.*?\'', strang[fixr:]); # Watch fixr
                
                if( regexr is not None ): # regexr is none if apophuph are unbalanced (so not a string)
                    nogo[0].append(regexr.start() + fixr); # Tack
                    nogo[1].append(regexr.end() + fixr - 1); # Tack
                    fixr += regexr.end(); # Move up
                else:
                    fixr += strang[fixr:].find("'") + 1; # Move past to yeet
                # END IF
            # END WHILE
            
            if( skipums is not None ):
                fixr = 0; # Reset
                for skipz in skipums:
                    skipzLoc = strang[fixr:].find(skipz);
                    while( skipzLoc > -1 ):
                        skipzLoc += fixr; # Fix it up, need to know about -1 so do this here
                        newlineLoc = strang[skipzLoc+1:].find('\n'); # Get the new line location, need to know about -1
                        if( any([(nogo[0][jj] < skipzLoc) and (nogo[1][jj] > skipzLoc) for jj in range(0, len(nogo[0]))]) ):
                            # Was within a string
                            fixr = skipzLoc + 1; # Move past it
                            skipzLoc = strang[fixr:].find(skipz);
                        elif( newlineLoc > -1 ):
                            newlineLoc += skipzLoc+2; # Based on the skipzLoc so can do it here (+1 for 1 past skipzLoc)
                            # Stuff after the line continuation, so end there
                            for jj in range(len(nogo[0])-1, -1, -1):
                                if( (nogo[0][jj] > skipzLoc) and (nogo[1][jj] <= newlineLoc) ):
                                    nogo[0].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                                    nogo[1].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                                # END IF
                            # END FOR jj
                            nogo[0].append(skipzLoc); # Add these bois on
                            nogo[1].append(newlineLoc);
                            
                            fixr = skipzLoc + 1; # Move past it
                            skipzLoc = strang[fixr:].find(skipz);
                        else:
                            # Not in a string or has a line continuation, everything after it is nuked
                            for jj in range(len(nogo[0])-1, -1, -1):
                                if( (nogo[0][jj] > skipzLoc) and (nogo[1][jj] <= len(strang)) ):
                                    nogo[0].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                                    nogo[1].pop(jj); # Yeet, it's in the skipums (prob apostrophe in a comment)
                                # END IF
                            # END FOR jj
                            nogo[0].append(skipzLoc); # Add these bois on
                            nogo[1].append(len(strang));
                            skipzLoc = -1; # Exit out
                        # END IF
                    # END WHILE
                # END FOR skipz
            # END IF
            
            if( stepUp is not None ):
                fixr = stepUp; # Lets the whole string be analyzed for comments/apopstrophes but only a bit be analyzed for matching
            else:
                fixr = 0; # Reset for this
            # END IF
            for jk in range(0, len(regexr_list)):
                regexr = re.search(regexStr, strang[fixr:]); # Watch fixr
                # if( any([(nogo[0][jj] < (regexr.start() + fixr)) and (nogo[1][jj] >= (regexr.end() + fixr - 1)) for jj in range(0, len(nogo[0]))]) ):
                # if( any([ ((nogo[0][jj] < (regexr.start() + fixr)) and (nogo[1][jj] >= (regexr.end() + fixr - 1))) or \
                #           (((nogo[0][jj] >= (regexr.start() + fixr)) and (nogo[0][jj] < (regexr.end() + fixr - 1))) or \
                #           ((nogo[1][jj] >= (regexr.start() + fixr)) and (nogo[1][jj] < (regexr.end() + fixr - 1)))) for jj in range(0, len(nogo[0]))]) ):
                if( any([ \
                        (((regexr.start() + fixr) >= nogo[0][jj]) and ((regexr.start() + fixr)  < nogo[1][jj])) or \
                        (((regexr.end() + fixr - 1) >= nogo[0][jj]) and ((regexr.end() + fixr - 1)  < nogo[1][jj])) \
                        for jj in range(0, len(nogo[0]))]) ):
                    # Was within a string or comment
                    fixr += regexr.end(); # Move past it
                    regexr_list[jk] = False;
                else:
                    # Real deal
                    regexr_list[jk] = fakeMatch(startV=regexr.start() + fixr, endV=regexr.end() + fixr, spanV=(regexr.start() + fixr, regexr.end() + fixr), groupV=regexr.group()) # Return somethat works like how I use it
                    fixr += regexr.end(); # Move up
                # END IF
            # END FOR jk
            
            if( FLG_logic == False ): # Report out as needed
                if( any(regexr_list) ):
                    if( FLG_rev == False ):
                        for jk in range(0, len(regexr_list)):
                            if( regexr_list[jk] != False ):
                                return regexr_list[jk] # Return first good match
                            # END IF
                        # END FOR jk
                    else:
                        for jk in range(len(regexr_list)-1, -1, -1):
                            if( regexr_list[jk] != False ):
                                return regexr_list[jk] # Return first good match
                            # END IF
                        # END FOR jk
                    # END IF
                else:
                    return None # Make it none if it didn't avoid
                # END IF
            else:
                if( any(regexr_list) ):
                    if( FLG_rev == False ):
                        for jk in range(0, len(regexr_list)):
                            if( regexr_list[jk] != False ):
                                return True # Did it!
                            # END IF
                        # END FOR jk
                    else:
                        for jk in range(len(regexr_list)-1, -1, -1): # Return last first instead of 1st first
                            if( regexr_list[jk] != False ):
                                return True # Did it!
                            # END IF
                        # END FOR jk
                    # END IF
                else:
                    return False # Nop
                # END IF
            # END IF
        # END IF
    else:
        if( FLG_logic == False ): # Report out as needed
            return None # Make it none
        else:
            return False # Nop
        # END IF
    # END IF
# END DEF

def regex_avoid_logic(regexStr, strang, skipums, FLG_rev = False):
    return regex_avoid(regexStr, strang, skipums, FLG_rev = False, FLG_logic = True) # Call this
# END DEF

def splitterz(strang, splitter, splitums):
    splot = []; # Holds the split
    
    # Identify no go zones
    nogo = [[], []]; # Prime list of lists
    
    # --- First apostrophes since they can hold anything, including # ---
    if( splitums is not None ):
        for splitz in splitums:
            fixr = 0; # Reset
            while( strang[fixr:].find(splitz[0]) > -1 ):
                # Apophuph time
                regexr = re.search(splitz[0].replace('[',r'\[').replace('(',r'\(')+r'.*?'+splitz[1].replace(']',r'\]').replace(')',r'\)'), strang[fixr:]); # Watch fixr
                
                if( regexr is not None ): # regexr is none if apophuph are unbalanced (so not a string)
                    nogo[0].append(regexr.start() + fixr); # Tack
                    nogo[1].append(regexr.end() + fixr - 1); # Tack
                    fixr += regexr.end(); # Move up
                else:
                    fixr += strang[fixr:].find(splitz[0]) + 1; # Move past to yeet
                # END IF
            # END WHILE
        # END FOR splitz
    # END IF
    
    FLG_GO = True; # VROOM VROOM
    fixr = 0; # Walk across the water
    fixr_last = 0; #hi its me youre all in danger
    while( FLG_GO ):
        findz = strang[fixr:].find(splitter);
        if( findz == -1 ):
            FLG_GO = False; # Yeet out
            splot.append(strang[fixr_last:]); # Tack on the rest
        elif( any([(nogo[0][jj] < (findz + fixr)) and (nogo[1][jj] >= (findz + fixr)) for jj in range(0, len(nogo[0]))]) ):
            # Was within a string or comment
            fixr += findz+1; # Move past it
        else:
            splot.append(strang[fixr_last:findz+fixr]); # Tack it on
            fixr += findz+1; # Move past it
            fixr_last = fixr; # Record last lock
        # END IF
    # END WHILE
    
    if( len(splot) == 0 ):
        splot = [strang]; # Just all of it
    # END IF
    return splot
# END DEF

def mirrorU( strang ): # Keeps a reversed string having () or [] or {} that actually face each other (regex loves it!)
    mirrorUniverse = ''; #yoinker
    for i in range(len(strang)-1, -1 ,-1):
        match strang[i]:
            case '[':
                mirrorUniverse += ']'; # Mirror universe
            case '(':
                mirrorUniverse += ')'; # Mirror universe
            case '{':
                mirrorUniverse += '}'; # Mirror universe
            case ']':
                mirrorUniverse += '['; # Mirror universe
            case ')':
                mirrorUniverse += '('; # Mirror universe
            case '}':
                mirrorUniverse += '{'; # Mirror universe
            case _:
                mirrorUniverse += strang[i]; #Add it on
            # END CASES
        # END MATCH
    # END FOR i
    return mirrorUniverse
# END DEF

def where_enclosed_parenthesis(strang, start, stop):
    parenLoc = strang[:start].rfind('(');
    while( parenLoc > -1 ):
        parenMatch = parenthesis_hunter(strang[parenLoc:]) + parenLoc; # Hunt the matching parenthesis location
        if( parenMatch < stop ):
            # It does not enclose stop
            fixr = start - parenLoc; # Move start back with fixr
            parenLoc = strang[:start-fixr].rfind('('); # Find a new loc
        else:
            return [parenLoc+1, parenMatch]
        # END IF
    # END WHILE
    
    return None # Not enclosed
# END DEF

def parenthesis_hunter( strang, charbroil=['(',')'] ):
    # Finds the index of the last matching parenthesis
    p_start = strang.find(charbroil[0])+1; # Go time
    parent_to_end = 1; # Set the number to 1
    for jj in range(p_start, len(strang)):
        if( strang[jj] == charbroil[0] ): # This was gonna be a match/case but cases can't be variables cause wtf python
            parent_to_end += 1; # It goes up
        elif( strang[jj] == charbroil[1] ):
            parent_to_end -= 1 ; # It goes down
        # END IF
        if( parent_to_end == 0 ): # Closed the loop
            return jj # Did it
        # END IF
    # END FOR jj
    # Got to here, did not close the loop
    return -1
# END DEF

def apophuph_hunter( strang, charbroil="'" ): # Like the parenthesis hunter, but for symmetrical stuff
    # Finds the index of the last matching apophuph
    p_start = strang.find(charbroil)+1; # Go time
    parent_to_end = 1; # Set the number to 1
    for jj in range(p_start, len(strang)): # Simpler b/c no nested strings
        if( strang[jj] == charbroil ):
            parent_to_end -= 1 ; # It goes down
        # END IF
        if( parent_to_end == 0 ): # Closed the loop
            return jj # Did it
        # END IF
    # END FOR jj
    # Got to here, did not close the loop
    return -1
# END DEF

def if_hunter( listOstrangs, indx, straddlers, skipums, recursiveMode=False ):
    # hoooo weeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee
    whereat = strisin_where( listOstrangs[indx].lower(), 'if', straddlers );
    # Determine if it's part of an if statement
    if( (len(whereat) > 0) and avoider( listOstrangs[indx][:whereat[0]], skipums ) ): # Got em
        if( 'then begin' in listOstrangs[indx].lower() ):
            # 'then begin' has an 'endif', time to hunt
            FLG_endelse = False;
            jk = indx+1; # Prime the cntr
            while( jk < len(listOstrangs) ):
                # hur we go
                # DEFEND AGAINST NESTED LOOPS!
                whereat = strisin_where( listOstrangs[jk].lower(), 'if', straddlers );
                # Determine if it's part of an if statement
                if( (len(whereat) > 0) and avoider( listOstrangs[jk][:whereat[0]], skipums ) ): # Got em
                    jk = if_hunter( listOstrangs, jk, recursiveMode=True ); # Skip by nested if loops
                else:
                    if( FLG_endelse == False ):
                        whereat = strisin_where( listOstrangs[jk].lower(), 'endif', straddlers );
                    else:
                        whereat = strisin_where( listOstrangs[jk].lower(), 'endelse', straddlers );
                    # END IF
                    # Determine if it's part of an if statement
                    if( (len(whereat) > 0) and avoider( listOstrangs[jk][:whereat[0]], skipums ) ): # Got em
                        if( FLG_endelse == False ):
                            whereat_elsebegin = strisin_where( listOstrangs[jk].lower(), 'else begin', straddlers );
                            whereat_else = strisin_where( listOstrangs[jk].lower(), 'else', straddlers );
                        else:
                            whereat_elsebegin = [];
                            whereat_else = []; # Stub em
                        # END IF
                        if( (len(whereat_elsebegin) > 0) and avoider( listOstrangs[jk][:whereat_elsebegin[0]], skipums ) ): # Got em
                            FLG_endelse = True; # Time to search for endelse, not done yet
                        elif( (len(whereat_elsebegin) == 0) and (len(whereat_else) > 0) and avoider( listOstrangs[jk][:whereat_else[0]], skipums ) ): # Got em
                            # Hunt this down, just based on $ line continuations
                            while( end_finder(idl[jk], '$', skipums) ):
                                jk += 1; # Increment
                            # END WHILE
                            # Donezo, hunted
                            break;
                        else:
                            # Donezo, hunted
                            break;
                        # END IF
                    # END IF
                # END IF
                
                jk +=1; # Increment
            # END WHILE (jk)
            
        else:
            # 'then' is a "one liner" that is often NOT one line (holla holla get $dolla$)
            jk = indx; # Prime the cntr
            while( end_finder(idl[jk], '$', skipums) ): # Go on till no more $ line continuations
                jk += 1; # Increment
            # END WHILE
        # END IF
        if( recursiveMode == True ):
            return jk
        else:
            return {'if at all':True,'start':indx,'stop':jk}
        # END IF
    else:
        # You don't call recursive mode if no if, so this won't happen
        return {'if at all':False,'start':None,'stop':None}
    # END IF
# END DEF

#!!!
def trans( idl, libDir = None ):
    # --- Prime reusables ---
    straddlers = [' ',',','+','=','-','*','/','^','<','>','[',']','(',')',':','\t','&','\'','"'] # These things can be right next to vars
    builtIns = ['print', 'message', 'printf', 'help', 'plot', 'xyouts', 'window', 'catch', 'strput', 'strcompress', 'readcol', 'sxaddpar', 'remchar']; # These are built-in functions that are not external functions
    forceImport = ['sphdist']; # These are called like a function() but aren't built-in functions but need to be imported, IDL tho am i right
    skipums = [';']; # These are things that allow for anyhting to be printed, so skip em and don't analyse
    skipums_py = ['#']; # These are things that allow for anyhting to be printed, so skip em and don't analyse
    splitums = [["'","'"], ['"', '"'], ['[',']']]; # THings that shouldn't be split
    dukeNukems = ['compile_opt', 'on_error', 'n_params()eq0']; # These are functions that must be removed
    proctedPy = dir(pyBuiltIns); # These are built-in Python functions that probably shouldn't be renamed by a variable in IDL
    proctedPy.extend(['np','scipy','pd','plt','os','sys','re','pickle']); # Any extras we want to avoid
    proctedPy_lower = [stringy.lower() for stringy in proctedPy]; # Convert all to lower, makes things easier for IDL stuff
    
    # --- Prime info holders ---
    spacer = 0; # Keep track of spacing
    codez = []; # No idea how big
    importz = {}; # Supported imports go here, tick to True when used and imported - autofilled, bottom reader deals with actual support for importing
    straddlersR = ''.join(straddlers).replace('+',r'\+').replace('-',r'\-').replace('*',r'\*').replace('[',r'\[').replace(']',r'\]').replace('(',r'\(').replace(')',r'\)'); # The straddlers in regex-friendly-form
    global convertedCache; # Summon the cache across multiple runs (so subcalls know about the cache)
    convertedCache_local = {}; # Prime this, this is functions local to this thing
    # Fixers for horrible code consistency in IDL
    FLG_IF_open = 0;
    FLG_ELSE_open = 0;
    FLG_FOR_open = 0;
    FLG_lastOpen = []; # Start this up
    # Helper functions
    importOffset = 0; # Remembers offset needed for inserting helper functions after imports
    FLG_FUN_idl_where_size = False; 
    FLG_FUN_idl_size_type = False; # Means that the function hasn't been added in if it is false
    FLG_FUN_idl_size_general = False;
    FLG_FUN_idl_size_structure = False;   
    FLG_FUN_idl_wait_key = False;    
    FLG_FUN_idl_strcompress = False;    
    FLG_FUN_idl_plt_gifWriter = False;
    FLG_FUN_idl_convol = False;
    
    # --- Nuke things that are not applicable to python ---
    for i in range(len(idl)-1, -1, -1):
        if( any(zz in idl[i].replace(' ','').lower() for zz in dukeNukems) ):
            # Time to nuke
            # See if it's in an if statement
            ifcheck = if_hunter( idl, i, straddlers, skipums ); # Hunt the if
            if( ifcheck['if at all'] == True ):
                # Nuke all lines involved
                for jk in range(ifcheck['stop'], i-1, -1):
                    idl.pop(jk); # Yeet into the aether
                # END FOR jk
            else:
                # Only need to duke nukem one line
                idl.pop(i); # Yeet into the aether
            # END IF
        # END IF
        
        # --- This fix is for apparently print statements strings DON'T NEED TO BE ENDED --------
        regexr_hangingStrang = regex_avoid( r'^\s*print *,', idl[i].lower(), skipums ); # Get to it
        if( regexr_hangingStrang is not None ):
            if( idl[i].find("'") > -1 ): # You can print just variables no strings, so don't add to those
                make_sure_it_match = apophuph_hunter( idl[i][regexr_hangingStrang.end():] ); # Get to it
                if( make_sure_it_match == -1 ):
                    regexr_comment = regex_avoid(r';', idl[i], None); # Regex it
                    if( regexr_comment is not None ):
                        idl[i] = strinsert( idl[i], regexr_comment.start()-1, "'"); # Jam it
                    else:
                        idl[i] += "'"; # Slam it
                    # END IF
                # END IF
            # END IF
        # END IF
        
        # --- Fix for returns that I didn't want to put elsewhere ---
        remove_comma = regex_avoid(r'^\s*return *,', idl[i].lower(), skipums);
        if( remove_comma is not None ):
            idl[i] = strreplace( idl[i], remove_comma.end()-1, remove_comma.end(), '');
        # END IF
        remove_caps = regex_avoid(r'^\s*RETURN', idl[i], skipums);
        if( remove_caps is not None ):
            idl[i] = strreplace( idl[i], remove_caps.end()-6, remove_caps.end(), 'return');
        # END IF
    # END FOR i
    
    # --- Figure out the included functions, can ignore looking for an import if it's included ---
    funName_included = []; # Keep the function names that are included
    i = 0; # While loop so i shennanigans can occur
    while( i < len(idl) ):
        bevItUp = idl[i]; # Yoink the line
        # --- Detect line continuation, combine ---
        while( end_finder(idl[i], '$', skipums) ):
            i += 1; # Increment
            if( regex_avoid_logic(r'\$', idl[i], skipums) and (not regex_avoid_logic(r'\$ *$', idl[i], skipums)) and (not regex_avoid_logic(r';', idl[i], None)) ):
                # Requires patching, apparently in IDL you can end a line continuation with a comment without needing the comment ;, coding to support that would be annoying - so I don't!
                # regexr = regex_avoid(r'\$', mirrorU(idl[i]), None); # Get where $ at
                # dollaLoc = len(idl[i]) - regexr.end(); # Un-mirror-universe it
                regexr = regex_avoid(r'\$', idl[i], skipums, FLG_rev=True); # Get where $ at
                idl[i] = strinsert(idl[i], regexr.start()+1, ' ;'); # Insert a comment
            # END IF            
            bevItUp += '\n '+idl[i]; # Tack on more!
        # END WHILE
        
        regexr_pro = regex_avoid(r'^\s*pro +', bevItUp.lower(), skipums); # Regex it
        regexr_fun = regex_avoid(r'^\s*function +', bevItUp.lower(), skipums); # Regex it
        if( (regexr_pro is not None) or (regexr_fun is not None) ):
            if( regexr_pro is not None ):
                pro = regexr_pro.start(); # Find pro occurance
                pro_len = regexr_pro.end() - regexr_pro.start();
            else:
                pro = regexr_fun.start(); # Find other fun occurance
                pro_len = regexr_fun.end() - regexr_fun.start();
            # END IF
            
            bevItUp = strreplace( bevItUp, pro, pro+pro_len, 'def.' ); # Replace pro with def (standardizes it)
            regexr_defy = regex_avoid(r'^\s*def.\w+,', bevItUp, skipums); # Regex it
            if( regexr_defy is not None ):
                defy = regexr_defy.end() - 1; # Find 1st comma occurance, signals function name
            else:
                regexr_defy = regex_avoid(r'^\s*def.\w+', bevItUp, skipums); # Regex it - there may be no comma in super special instances apparently
                defy = regexr_defy.end(); # No comma, go to end
            # END IF
            # builtIns.append(bevItUp[pro+pro_len:defy]); # Function name included, add it to the built-ins
            funName_included.append(bevItUp[4:defy]); # Function name included, add it to the included (superceeds looking for it in libraries)
        # END IF
            
        i += 1; # Move up
    # END WHILE
    
    i = 0; # While loop so i shennanigans can occur
    while( i < len(idl) ):
        FLG_spacer = 0; # Set the spacing flag
        bevItUp = idl[i]; # Yoink the line        
        addr = 0; # Record how much
        # --- Detect line continuation, combine ---
        while( end_finder(idl[i], '$', skipums) ):
            i += 1; # Increment
            addr += 1; # Increment
            if( regex_avoid_logic(r'\$', idl[i], skipums) and (not regex_avoid_logic(r'\$ *$', idl[i], skipums)) and (not regex_avoid_logic(r';', idl[i], None)) ):
                # Requires patching, apparently in IDL you can end a line continuation with a comment without needing the comment ;, coding to support that would be annoying - so I don't!
                # regexr = regex_avoid(r'\$', mirrorU(idl[i]), None); # Get where $ at
                # dollaLoc = len(idl[i]) - regexr.end(); # Un-mirror-universe it
                regexr = regex_avoid(r'\$', idl[i], skipums, FLG_rev=True); # Get where $ at
                idl[i] = strinsert(idl[i], regexr.start()+1, ' ;'); # Insert a comment
            # END IF            
            bevItUp += '\n '+idl[i]; # Tack on more!
        # END WHILE
        regexr = regex_avoid(r'\$+? *?;+?.*?\n+?', bevItUp, None); # Find comments on line continuations, which are illegal in Python (full lazy mode)
        while( regexr is not None ):
            lostComment = bevItUp[regexr.start()+1:regexr.end()-1]; # Catch that lost comment
            bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), '$\n'); # Laser eyes the lost comment
            bevItUp += lostComment; # Slap it at the end, which is cool
            
            regexr = regex_avoid(r'\$+? *?;+?.*?\n+?', bevItUp, None); # Find comments on line continuations, which are illegal in Python (full lazy mode)
        # END IF
        
        #!!!
        # --- Deal with function definition (pro) lines ---
        regexr_pro = regex_avoid(r'^\s*pro +', bevItUp.lower(), skipums); # Regex it
        regexr_fun = regex_avoid(r'^\s*function +', bevItUp.lower(), skipums); # Regex it
        if( (regexr_pro is not None) or (regexr_fun is not None) ):
            if( regexr_pro is not None ):
                pro = regexr_pro.start(); # Find pro occurance
                pro_len = regexr_pro.end() - regexr_pro.start();
            else:
                pro = regexr_fun.start(); # Find other fun occurance
                pro_len = regexr_fun.end() - regexr_fun.start();
            # END IF
            
            bevItUp = strreplace( bevItUp, pro, pro+pro_len, 'def.' ); # Replace pro with def (standardizes it)
            regexr_defy = regex_avoid(r'^\s*def.\w+,', bevItUp, skipums); # Regex it
            if( regexr_defy is not None ):
                defy = regexr_defy.end() - 1; # Find 1st comma occurance, signals function name
            else:
                regexr_defy = regex_avoid(r'^\s*def.\w+', bevItUp, skipums); # Regex it - there may be no comma in super special instances apparently
                defy = regexr_defy.end(); # No comma, go to end
            # END IF
            # builtIns.append(bevItUp[4:defy]); # Function name right now, add it to the built-ins
            funName_now = bevItUp[4:defy]; # It's the fun name right now
            funt = i-addr; # Function start

            bevItUp = strreplace1( bevItUp, defy, '('); # Replace , with (

            regexr = regex_avoid(r'\w+ *;', bevItUp, skipums); # Regex it
            if( regexr is not None ):
                bevItUp = strinsert( bevItUp, regexr.end()-1, ') '); # Slap on
                regexr_spacer = regex_avoid(r' {2,}', bevItUp, skipums); # Regex it
                while( regexr_spacer is not None ): # Clean up spacing
                    bevItUp = strreplace(bevItUp, regexr_spacer.start(), regexr_spacer.end(), ' '); # Reduce the spaces
                    regexr_spacer = regex_avoid(r' {2,}', bevItUp, skipums); # Regex it
                # END WHILE
            else:
                bevItUp = bevItUp.rstrip(' '); # Clean it up
                commenty = bevItUp.find(';'); # Find a comment in the line
                # Clean up commas
                if( commenty > -1 ):
                    bevItUp = strreplace(bevItUp, commenty-1, commenty, ' )'); # No spaces, it helps with the fixed-width lookbehind requirement
                else:
                    bevItUp += ' )'; # Add an ending )
                # END IF
            # END IF
            
            # Detect outputs and get them out of the inputs
            defy_ins = []; # Time to find out
            fixr = defy+1; # Fix it up (move past the function definition)
            regexr = regex_avoid(r'(\w+ *,|\w+ *= *\w+ *,|\w+ *\)|\w+ *= *\w+ *\)|, *\w+|, *\w+ *= *\w+)', bevItUp, skipums, stepUp=fixr); # Regex it
            while( regexr is not None ):
                defy_ins.append(bevItUp[regexr.start():regexr.end()-1].rstrip(' ')); # Slap it in
                fixr = regexr.end(); # Move it up
                regexr = regex_avoid(r'(\w+ *,|\w+ *= *\w+ *,|\w+ *\)|\w+ *= *\w+ *\)|, *\w+|, *\w+ *= *\w+)', bevItUp, skipums, stepUp=fixr); # Regex it
            # END WHILE
            defy_outs = []; # Who knows!
            defy_unused = []; # It happens
            importedMemory = []; # Remembers if a called function is imported (helps with calling multiple times)
            FLG_plt_windowCalled = False; # Prime the window remeberall based on the function
            FLG_plt_gifWriter = False; # Prime the gif writer rememberall
            FLG_plt_gifWriter_names = []; # Important if multiple gif writers are used at once, can it happen? Maybe?
            FLG_elif = False; # Tracks elifs
            FLG_elifSplitLine = False; # Tracks split lines that are elif but the thing can't figure that out (not my fault)
            FLG_case = False; # Prime the case remeberall based on the function
            FLG_case_accursedIf = False; # Prime the case-accursed-if remeberall based on the function
            # FLG_case_thenWithNoBegin = False; # Prime the case including a begin call rememerall
            FLG_caseIf = False; #it's a case if which means it's weird
            # FLG_caseClosed = False; # Prime the case rememberall for if an else call closes the if statement or not
            
            # Start of function noted
            rando_varr_num = 0; # Increment this as needed
            #--- Scan for end of function to know where it end (allows for multiple functions per file) ---
            for jk in range(i+1, len(idl)):
                # end!
                regexrL = regex_avoid_logic(r'^\s*end', idl[jk].lower(), skipums) and strisin( idl[jk].lstrip('\t').lstrip(' ').lower(), 'end', straddlers ); # Regex it
                if( regexrL ):
                    fend = jk+1; # Record where the function/PROOO ends (+1 for SLICIN'), use it to limit later stuff
                    break; # ditch it
                # END IF
            # END FOR jk
            
            for j in range(0, len(defy_ins)):
                
                FLG_used = False; # Re-prime this
                FLG_defaults_neverUsed = False; # Re-prime this
                
                if( defy_ins[j].find('=') == -1 ):
                    searchr = defy_ins[j]; # Look for this
                    FLG_defaulted = False; # Re-prime this
                else:
                    # Caught a "default" assignment, which is kinda cursed tbh
                    searchr = defy_ins[j].split('='); # Use this as a temp var
                    searchr[0] = searchr[0].strip(' '); # Fix spacing issues
                    searchr[1] = searchr[1].strip(' '); # Fix spacing issues
                    FLG_defaulted = True; # It's a default!
                    
                    # Pre-game shining up
                    # --- Catch stuff like 'MMM=mmm' which means nothing ---
                    if( searchr[0].isupper() and ((searchr[0].lower() == searchr[1]) or (searchr[0] == searchr[1])) ):
                        # Detect if lower is used as a function (yeah this is a real deal)
                        FLG_isFun = False; # Prime up
                        for jk in range(i+1, fend):
                            if( strisin(idl[jk], searchr[1], straddlers) ):
                                FLG_isFun = idl[jk].lstrip('\t').lstrip(' ')[:len(searchr[1])+1] == searchr[1]+',' or FLG_isFun; # It's a function
                            # END IF
                        # END FOR jk
                        
                        # Replace MMM uses with mmm
                        if( FLG_isFun == False ):
                            if( searchr[0] == searchr[1] ):
                                searchr[1] = searchr[1].lower(); # Enforce
                            # END IF
                            
                            for jk in range(i+1, fend):
                                searchr_isin_where = strisin_where(idl[jk], searchr[0], straddlers);
                                if( len(searchr_isin_where) > 0 ):
                                    if( avoider( idl[jk][:searchr_isin_where[0]], skipums ) ): # Don't mess with comments or prints, no need
                                        idl[jk] = strreplace( idl[jk], searchr_isin_where[0], searchr_isin_where[1], searchr[1] ); # Replace capital one with lower case for standardardizing (they do it a lot)
                                    # END IF
                                # END IF
                            # END FOR jk
                            
                            # Rename in process, rename in bevItUp
                            regexr_repy = regex_avoid(searchr[0]+r' *=', bevItUp, skipums); # Regex it
                            bevItUp = strreplace( bevItUp, regexr_repy.start(), regexr_repy.end(), searchr[1]+' =' ); # Replace with new name
                            
                            searchr = searchr[1].lower(); # Standardized to lower case!
                        else:
                            regexr_repy = regex_avoid(searchr[0]+r' *=', bevItUp, skipums); # Regex it
                            searchr = searchr[0].lower(); # Use all caps b/c lower case is a function (no change)
                            bevItUp = strreplace( bevItUp, regexr_repy.start(), regexr_repy.end(), searchr+' =' ); # Replace with new name
                        # END IF
                    else:
                        # If they essentially share the same name, see if searchr[0] is used at all - often it's not
                        FLG_searchr_used = False;
                        for jk in range(i+1, fend):
                            searchr_isin_where = strisin_where(idl[jk], searchr[0], straddlers);
                            if( (len(searchr_isin_where) > 0) and ( avoider( idl[jk][:searchr_isin_where[0]], skipums ) or ( avoider_finder( idl[jk][:searchr_isin_where[0]], skipums ) < idl[jk][:searchr_isin_where[0]].find('\'') ) ) ):
                                FLG_searchr_used = True; # Found it
                                break; # Yeet
                            # END IF
                        # END FOR jk
                        if( FLG_searchr_used == True ):
                            if( searchr[0] == searchr[0].upper() ):
                                regexr_repy = regex_avoid(searchr[0]+r' *=', bevItUp, skipums); # Regex it
                                bevItUp = strreplace( bevItUp, regexr_repy.start(), regexr_repy.end(), searchr[1]+' =' ); # Replace with new name
                                
                                if( searchr[1] == searchr[1].upper() ):
                                    searchr = searchr[1].lower(); # Standardized to lower case since the non-lower-case is always used
                                else:
                                    searchr = searchr[1]; # Good to go
                                # END IF
                                for jk in range(i+1, fend):
                                    searchr_isin_where = strisin_where(idl[jk].lower(), searchr.lower(), straddlers);
                                    if( (len(searchr_isin_where) > 0) and ( avoider( idl[jk][:searchr_isin_where[0]], skipums ) or ( avoider_finder( idl[jk][:searchr_isin_where[0]], skipums ) < idl[jk][:searchr_isin_where[0]].find('\'') ) ) ):
                                        idl[jk] = strreplace( idl[jk], searchr_isin_where[0], searchr_isin_where[1], searchr ); # Replace capital one with lower case for standardardizing (they do it a lot)
                                    # END IF
                                # END FOR jk
                            else:
                                searchr = searchr[0]; # Keep it, it is used!
                                for jk in range(i+1, fend):
                                    searchr_isin_where = strisin_where(idl[jk].lower(), searchr.lower(), straddlers);
                                    if( (len(searchr_isin_where) > 0) and ( avoider( idl[jk][:searchr_isin_where[0]], skipums ) or ( avoider_finder( idl[jk][:searchr_isin_where[0]], skipums ) < idl[jk][:searchr_isin_where[0]].find('\'') ) ) ):
                                        idl[jk] = strreplace( idl[jk], searchr_isin_where[0], searchr_isin_where[1], searchr ); # Replace capital one with lower case for standardardizing (they do it a lot)
                                    # END IF
                                # END FOR jk
                            # END IF
                        else:
                            # Rename in process, rename in bevItUp
                            regexr_repy = regex_avoid(searchr[0]+r' *=', bevItUp, skipums); # Regex it
                            bevItUp = strreplace( bevItUp, regexr_repy.start(), regexr_repy.end(), searchr[1]+' =' ); # Replace with new name
                            
                            if( searchr[1] == searchr[1].upper() ):
                                searchr = searchr[1].lower(); # Standardized to lower case since the non-lower-case is always used
                            else:
                                searchr = searchr[1]; # Good to go
                            # END IF
                            for jk in range(i+1, fend):
                                searchr_isin_where = strisin_where(idl[jk], searchr, straddlers);
                                if( (len(searchr_isin_where) > 0) and ( avoider( idl[jk][:searchr_isin_where[0]], skipums ) or ( avoider_finder( idl[jk][:searchr_isin_where[0]], skipums ) < idl[jk][:searchr_isin_where[0]].find('\'') ) ) ):
                                    idl[jk] = strreplace( idl[jk], searchr_isin_where[0], searchr_isin_where[1], searchr ); # Replace capital one with lower case for standardardizing (they do it a lot)
                                # END IF
                            # END FOR jk
                        # END IF
                    # END IF
                    
                    #--- Check if it's used as a keyword check only ---
                    searchr_keyword = r'(keyword_set|KEYWORD_SET)\( *'+searchr+r' *\)';
                    FLG_usedAtAll = False;
                    FLG_keyword = True;
                    for jk in range(i+1, fend):
                        searchr_isin_where = strisin_where( idl[jk], searchr, straddlers );
                        if( len(searchr_isin_where) > 0 ): # See if in it
                            FLG_usedAtAll = True; # important
                            if( avoider( idl[jk][:searchr_isin_where[0]], skipums ) & (not regex_avoid_logic(searchr_keyword, idl[jk], skipums)) ): # Make sure not in a comment and not a keyword (to know it's not used as a keyword only!)
                                FLG_keyword = False;
                                if( regex_avoid_logic(r'^\s*'+searchr+r' *,', idl[jk], skipums) ): # Catches if it's actually a function call - can happen, a default input named the function used as a switch to activat ethe function or not
                                    FLG_keyword = True; # Back to this
                                    # Now we need to rename everything but the function call
                                    for jkjk in range(i+1, fend):
                                        fixr = 0;
                                        regexr_strad = regex_avoid('((?:['+straddlersR+']|^)'+searchr.lower()+'(?:['+straddlersR+']|$))', idl[jkjk].lower(), skipums); # Regex it
                                        if( (regexr_strad is not None) and (not regex_avoid_logic(r'^\s*'+searchr.lower()+r' *,', idl[jkjk].lower(), skipums)) ):
                                            if( idl[jkjk][regexr_strad.start()] in straddlersR ):
                                                sharty = regexr_strad.start()+1; # Remove one
                                            else:
                                                sharty = regexr_strad.start(); # Keep cause it's the start
                                            # END IF
                                            if( idl[jkjk][regexr_strad.end()-1] in straddlersR ):
                                                endy = regexr_strad.end()-1; # Remove one
                                            else:
                                                endy = regexr_strad.end(); # Keep cause it's the end
                                            # END IF
                                            idl[jkjk] = strreplace(idl[jkjk], sharty, endy, searchr.lower()+'y'); # Replace it so it's unique
                                            fixr = endy+1; # Move fixr up
                                            regexr_strad = regex_avoid('((?:['+straddlersR+']|^)'+searchr.lower()+'(?:['+straddlersR+']|$))', idl[jkjk].lower(), skipums, stepUp=fixr); # Regex it
                                        # END WHILE
                                    # END FOR jkjk
                                    defy_ins[j] = searchr.lower()+'y='+searchr.lower()+'y'; # Replace defy_ins
                                    regexr_replr = regex_avoid(searchr+r' *=', bevItUp, skipums); # Regex it (deals with more in the same line)
                                    regexr_replr2 = regex_avoid(r'= *[\w_]* *[,|\)]', bevItUp, skipums, stepUp=regexr_replr.end()-1); # Regex it (deals with more in the same line)
                                    bevItUp = strreplace(bevItUp, regexr_replr.start(), regexr_replr2.end()-1, searchr.lower()+'y = '+searchr.lower()+'y '); # Update to none if the unused default value is the original variable name
                                    searchr = searchr.lower()+'y'; # Replace searchr
                                    searchr_keyword = r'(keyword_set|KEYWORD_SET)\( *'+searchr+r' *\)'; # Replace searchr_keyword
                                # END IF
                            # END IF
                        # END IF
                    # END FOR jk
                    if( (FLG_keyword == True) and (FLG_usedAtAll == True) ):
                        # Rename in process, rename in bevItUp
                        regexr_realz = regex_avoid(searchr+r' *=', bevItUp, skipums); # Regex it
                        regexr_repy = regex_avoid(r'= *\w+ *', bevItUp[regexr_realz.end()-1:], skipums); # Regex it
                        bevItUp = strreplace( bevItUp, regexr_repy.start() + regexr_realz.end()-1, regexr_repy.end() + regexr_realz.end()-1, '= False'); # Replace with new name
                        
                        defy_ins[j] = searchr + ' = False'; # If it's used as a keyword only, set it to be False (logical)
                        for jk in range(i+1, fend): # Replace keyword_set stuff with python logic using True/False (do it here since we know the most about it and don't need to assume as much if done later)
                            searchr_isin_where = strisin_where( idl[jk], searchr, straddlers );
                            if( len(searchr_isin_where) > 0 ): # See if in it
                                if( avoider( idl[jk][:searchr_isin_where[0]], skipums ) & regex_avoid_logic(searchr_keyword, idl[jk], skipums) ): # Make sure not in a comment and not a keyword (to know it's not used as a keyword only!)
                                    regexr = regex_avoid(searchr_keyword, idl[jk], skipums); # Regexr it
                                    strStart = regexr.start();
                                    strEnd = regexr.end();
                                    # strStart = idl[jk].find('keyword_set');
                                    # strEnd = idl[jk][strStart + len('keyword_set'):].find(')') + strStart + len('keyword_set') + 1; # For the end for pythn
                                    if( strStart > 0 ):
                                        FLG_notted = idl[jk][strStart-1] == '~'; # It's been notted!
                                    else:
                                        FLG_notted = False; # Cannot be if it is the start (which shouldn't happen but whatever)
                                    # END IF
                                    if( strisin( idl[jk][strStart:strEnd] , searchr, straddlers ) and (FLG_notted == False) ):
                                        idl[jk] = strreplace( idl[jk], strStart, strEnd, '( '+searchr+' == True )' ); # Replace time!
                                    elif( strisin( idl[jk][strStart:strEnd] , searchr, straddlers ) and (FLG_notted == True) ):
                                        idl[jk] = strreplace( idl[jk], strStart, strEnd, '( '+searchr+' == False )' ); # Replace time!
                                    else:
                                        print('This shouldn\'t have happened. Needs some extra code to account for this.');
                                        print('Line indx in idl (jk): '+str(jk)+'\nLine (idl[jk]): '+idl[jk]+'\nLine snippet: '+ \
                                              idl[jk][strStart:strEnd]+'\nSearch prev snippet for: '+searchr+'\nstraddlers defined: '+str(straddlers))
                                        breakpoint() # Yeet
                                    # END IF
                                # END IF
                            # END IF
                        # END FOR jk
                    elif( (FLG_keyword == False) and (FLG_usedAtAll == True) ):
                        # It's used NOT as a keyword
                        # Rename in process, rename in bevItUp
                        regexr_realz = regex_avoid(searchr+r' *=', bevItUp, skipums); # Regex it
                        regexr_repy = regex_avoid(r'= *\w+ *', bevItUp[regexr_realz.end()-1:], skipums); # Regex it
                        bevItUp = strreplace( bevItUp, regexr_repy.start() + regexr_realz.end()-1, regexr_repy.end() + regexr_realz.end()-1, '= None'); # Replace with new name
                        
                        defy_ins[j] = searchr + ' = None'; # If it's used as more than just a keyword, set it to be None
                        for jk in range(i+1, fend): # Replace keyword_set stuff with python logic using True/False (do it here since we know the most about it and don't need to assume as much if done later)
                            regexr_keyword = regex_avoid(r'keyword_set *\( *'+searchr+r' *\)', idl[jk], skipums); # Regex it
                            regexr_keywordN = regex_avoid(r'~ *keyword_set *\( *'+searchr+r' *\)', idl[jk], skipums); # Regex it
                            if( regexr_keywordN is not None ):
                                idl[jk] = strreplace( idl[jk], regexr_keywordN.start(), regexr_keywordN.end(), '( '+searchr+' is None )' ); # Replace time!
                            elif( regexr_keyword is not None ):
                                idl[jk] = strreplace( idl[jk], regexr_keyword.start(), regexr_keyword.end(), '( '+searchr+' is not None )' ); # Replace time!
                            # END IF
                        # END FOR jk
                    else:
                        # Otherwise it was never used at all...
                        print(defy_ins[j]+' was never used!');
                        # defy_ins[j] = defy_ins[j][:defy_ins[j].find('=')]+' = None'; # Make it an OK default
                        regexr_replr = regex_avoid(searchr+r' *=', bevItUp, skipums); # Regex it (deals with more in the same line)
                        regexr_replr = regex_avoid(r'= *[\w_]* *[,|\)]', bevItUp, skipums, stepUp=regexr_replr.end()-1); # Regex it (deals with more in the same line)
                        if( searchr.lower() == bevItUp[regexr_replr.start()+1:regexr_replr.end()-1].strip(' ').lower() ):
                            bevItUp = strreplace(bevItUp, regexr_replr.start(), regexr_replr.end()-1, '= None'); # Update to none if the unused default value is the original variable name
                        # END IF
                        FLG_defaults_neverUsed = True;
                    # END IF
                # END IF
                
                if( FLG_defaults_neverUsed == False ):
                    for jk in range(i+1, fend):
                        regexr = regex_avoid(r'((?:['+straddlersR+']|^)'+searchr+r'(?:['+straddlersR+']|$))', idl[jk], skipums); # Regex it (deals with more in the same line)
                        
                        # --- Check for unused inputs ---
                        if( (FLG_used == False) & (regexr is not None) ):                        
                            FLG_used = True; # Gottem
                        # END IF
                        
                        # --- Do some stuff if it's not a defaulted input (e.g., MMM=None)
                        if( FLG_defaulted == False ):
                            # --- Check for inputs that are actually outputs ---
                            regexr_eq = regex_avoid(r'(^\s*'+searchr+r' *=|& *'+searchr+r' *=)', idl[jk], skipums); # Regex it (deals with more in the same line)
                            if( regexr_eq is not None ):
                                FLG_actuallyOut = True; # Prime this up
                                for kj in range(jk-1, i, -1):
                                    regexr_strad = regex_avoid('((?:['+straddlersR+']|^)'+searchr+'(?:['+straddlersR+']|$))', idl[kj], skipums); # Regex it (deals with more in the same line)
                                    if( regexr_strad is not None ):
                                        regexr_strad = regex_avoid('((?:['+straddlersR+']|^)'+searchr+'(?:['+straddlersR+']|$))', idl[kj], skipums); # Regex it (deals with more in the same line)
                                        FLG_actuallyOut = False;
                                    # END IF
                                # END FOR kj
                                if( FLG_actuallyOut ):
                                    defy_outs.append(defy_ins[j]); # It's an output!
                                # END IF
                                FLG_used = True; # It was used!
                                break; # Yeet, no more need to check on it
                            # END IF
                        # END IF
                        # --- Check for inputs that are actually outputs from OTHER functions (yeah it gets nasty now) ---
                        # alexa laser eyes idl
                        FLG_forceFun = r','; # Flag for forced function
                        regexr_fun = regex_avoid(r'^\s*\w+ *,', idl[jk], skipums); # Regex it
                        if( regexr_fun is None ):
                            for jj in range(0, len(forceImport)):
                                regexr_fun = regex_avoid(forceImport[jj]+r' *\(', idl[jk], skipums); # Regex it
                                if( regexr_fun is not None ):
                                    FLG_forceFun = r'\('; # Special time
                                    break; # Yeet out
                                # END IF
                            # END FOR jj
                        # END IF
                        # if( (found > -1) & avoider( idl[jk][:found], skipums ) ):
                        if( (regexr is not None) and (regexr_fun is not None) ):
                            # Remove the front stuff
                            regexr_fun = regex_avoid(r'\w+ *'+FLG_forceFun, idl[jk][:regexr_fun.end()], skipums); # Regex it
                            funName = idl[jk][regexr_fun.start():regexr_fun.end()-1].strip(' ').lower(); # Get the function name
                            
                            regexr_fun_avoidRecurse = False;
                            for gg in range(funt, fend):
                                regexr_fun_avoidRecurse |= regex_avoid(r'^\s*pro *'+funName.lower()+r' *,', idl[gg].lower(), None, FLG_logic = True); # Regex it
                            # END FOR gg
                            if( funName == 'fxaddpar' ):
                                regexr_fun_avoidRecurse = True; # This one calls another function within that calls back to it, so that's hard to ponder so I'm just moving on for now
                            # END IF
                            if( regexr_fun_avoidRecurse == True ):
                                print('WARNING: "'+funName+'.pro" calls itself recursively and will NOT be analysed!');
                            # END IF
                            if( (regexr_fun_avoidRecurse == False ) and ((funName in convertedCache) or ((funName in funName_included) and (funName != funName_now))) ): # Rev up the cache to check it
                                # Get the report var outa the cache, no need to read it again
                                if( funName in convertedCache ):
                                    defy_report_fun = convertedCache[funName]['report'];
                                    
                                    # --- Insert the import as needed ---
                                    if( funName not in importedMemory ):
                                        if( libDir == None ):
                                            codez.insert(0, 'from '+funName+' import '+funName ); # Get the import at the top
                                        else:
                                            codez.insert(0, 'from '+os.path.basename(libDir)+'.'+funName+' import '+funName ); # Get the import at the top
                                        # END IF
                                        importOffset += 1; # Increment the offset
                                        importedMemory.append(funName); # Add it on
                                    # END IF
                                else:
                                    # Then it's in funName_included
                                    defy_report_fun = convertedCache_local[funName]['report'];
                                # END IF
                                
                                # --- Ascertain which are inputs or outputs or whatever ---
                                rejiggered = idl[jk][regexr_fun.end():]; # Split it up (will need more when there's a line continuation
                                if( rejiggered.find(';') > -1 ):
                                    rejiggered = rejiggered[:rejiggered.find(';')]; # Yeet this off
                                # END IF
                                rejiggered = rejiggered.split(','); # Break it apart
                                rejiggered = [bitty.strip(' ') for bitty in rejiggered]; # Make sure no spaces
                                rejiggered_defs = [None for _ in rejiggered]; # Prep this
                                for gg in range(0, len(rejiggered)):
                                    if( rejiggered[gg].find('=') > -1 ):
                                        rejiggered_defs[gg] = 'default;'+rejiggered[gg][:rejiggered[gg].find('=')]; # Yee boi
                                    else:
                                        rejiggered_defs[gg] = defy_report_fun[gg]; # Use it directly
                                    # END IF
                                # END FOR gg
                                
                                # --- Convert the line ---
                                rejiggered_ins = [];
                                rejiggered_outs = [];
                                rejiggered_defaults = [];
                                for gg in range(0, len(rejiggered)):
                                    if( rejiggered_defs[gg] == 'input' ):
                                        rejiggered_ins.append(rejiggered[gg]); # Tack it on
                                    elif( rejiggered_defs[gg] == 'output' ):
                                        rejiggered_outs.append(rejiggered[gg]); # Tack it on
                                    elif( 'default;' in rejiggered_defs[gg] ):
                                        if( '/' in rejiggered[gg] ):
                                            # Catch this switch thing, use the var name after / and set to True, it's a switch
                                            rejiggered_defaults.append(rejiggered[gg][rejiggered[gg].find('/')+1:]+' = True'); # Tack it on
                                        else:
                                            rejiggered_defaults.append(rejiggered[gg]); # Tack it on
                                        # END IF
                                    # END IF
                                # END FOR gg
                                if( FLG_forceFun == r',' ):
                                    if( idl[jk].find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                        idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                        if( len(rejiggered_defaults) > 0 ):
                                            idl[jk] += ', '+', '.join(rejiggered_defaults)+' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                        else:
                                            idl[jk] += ' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                        # END IF
                                    else:
                                        idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                        if( len(rejiggered_defaults) > 0 ):
                                            idl[jk] += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                        else:
                                            idl[jk] += ' )'; # Badabing, badaboom
                                        # END IF
                                    # END IF
                                    if( len(rejiggered_outs) == 0 ):
                                        regexr_emptyEq = regex_avoid(r'^\s*= *', idl[jk], skipums);
                                        if( regexr_emptyEq is not None ):
                                            idl[jk] = strreplace(idl[jk], regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                        # END IF
                                    # END IF
                                else:
                                    # This was called as a function so check for an ='s and if it's there don't bother
                                    if( idl[jk].find('=') > -1 ):
                                        paren_match = parenthesis_hunter(idl[jk][regexr_fun.start():])+regexr_fun.start();
                                        bit_inside = idl[jk][regexr_fun.end():paren_match].split(',');
                                        for jj in range(0, len(bit_inside)):
                                            bit_inside[jj] = bit_inside[jj].strip(' ');
                                            if( bit_inside[jj][0] == '/' ):
                                                bit_inside[jj] = bit_inside[jj][1:]+' = True'; # Make it better
                                            # END IF
                                        # END FOR jj
                                        bit_inside = ', '.join(bit_inside); # REBUILD
                                        idl[jk] = strreplace(idl[jk], regexr_fun.end(), paren_match, bit_inside)
                                    else:
                                        if( idl[jk].find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                            idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                            if( len(rejiggered_defaults) > 0 ):
                                                idl[jk] += ', '+', '.join(rejiggered_defaults)+' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                            else:
                                                idl[jk] += ' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                            # END IF
                                        else:
                                            idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                            if( len(rejiggered_defaults) > 0 ):
                                                idl[jk] += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                            else:
                                                idl[jk] += ' )'; # Badabing, badaboom
                                            # END IF
                                        # END IF
                                        if( len(rejiggered_outs) == 0 ):
                                            regexr_emptyEq = regex_avoid(r'^\s*= *', idl[jk], skipums);
                                            if( regexr_emptyEq is not None ):
                                                idl[jk] = strreplace(idl[jk], regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                            # END IF
                                        # END IF
                                    # END IF
                                # END IF
                                
                                FLG_used = True; # It was used!
                                
                            elif( (regexr_fun_avoidRecurse == False ) and (funName not in builtIns) ):
                                # --- Determine function file and where it at ---
                                # Look in the library paths
                                finds = glob(os.path.join(os.getcwd(),'**',funName+'.pro'), recursive=True); # Glob it up
                                if( len(finds) > 0 ):
                                    # --- Read in IDL file ---
                                    with open(finds[0], 'r') as file: # use 1st hit
                                        idl_fun = [line.rstrip() for line in file];
                                    # END WITH

                                    # --- Rip into it ---
                                    # Even if it is already converted, need defy_report to know if things are 
                                    print('\n--- ON '+finds[0]+' ---');
                                    codez_fun, defy_report_fun = trans( idl_fun, libDir = libDir ); # Translate from IDL to Python (in function form so can recursive if it finds OTHER IDL files)
                                    convertedCache[funName] = {'report':defy_report_fun}; # Cache it for later, only need this thing to convert a function

                                    # --- Save converted Python ---
                                    # finds = glob(os.path.join(os.getcwd(),'**',funName+'.py'), recursive=True); # Glob it up (this was to check if already had it written, but it might need updating or something so might as well just do it)
                                    if( libDir == None ):
                                        with open(os.path.join(os.getcwd(),funName+'.py'), 'w') as file:
                                            file.write('\n'.join(linez for linez in codez_fun));
                                        # END WITH
                                    else:
                                        with open(os.path.join(libDir,funName+'.py'), 'w') as file:
                                            file.write('\n'.join(linez for linez in codez_fun));
                                        # END WITH
                                     # END IF
                                    
                                    # --- Insert the import as needed ---
                                    if( funName not in importedMemory ):
                                        if( libDir == None ):
                                            codez.insert(0, 'from '+funName+' import '+funName ); # Get the import at the top
                                        else:
                                            codez.insert(0, 'from '+os.path.basename(libDir)+'.'+funName+' import '+funName ); # Get the import at the top
                                        # END IF
                                        importOffset += 1; # Increment the offset
                                        importedMemory.append(funName); # Add it on
                                    # END IF
                                    
                                    # --- Ascertain which are inputs or outputs or whatever ---
                                    rejiggered = idl[jk][regexr_fun.end():]; # Split it up (will need more when there's a line continuation
                                    if( rejiggered.find(';') > -1 ):
                                        rejiggered = rejiggered[:rejiggered.find(';')]; # Yeet this off
                                    # END IF
                                    rejiggered = rejiggered.split(','); # Break it apart
                                    rejiggered = [bitty.strip(' ') for bitty in rejiggered]; # Make sure no spaces
                                    rejiggered_defs = [None for _ in rejiggered]; # Prep this
                                    for gg in range(0, len(rejiggered)):
                                        if( rejiggered[gg].find('=') > -1 ):
                                            rejiggered_defs[gg] = 'default;'+rejiggered[gg][:rejiggered[gg].find('=')]; # Yee boi
                                        else:
                                            rejiggered_defs[gg] = defy_report_fun[gg]; # Use it directly
                                        # END IF
                                    # END FOR gg
                                    
                                    # --- Convert the line ---
                                    rejiggered_ins = [];
                                    rejiggered_outs = [];
                                    rejiggered_defaults = [];
                                    for gg in range(0, len(rejiggered)):
                                        if( rejiggered_defs[gg] == 'input' ):
                                            rejiggered_ins.append(rejiggered[gg]); # Tack it on
                                        elif( rejiggered_defs[gg] == 'output' ):
                                            rejiggered_outs.append(rejiggered[gg]); # Tack it on
                                        elif( 'default;' in rejiggered_defs[gg] ):
                                            if( '/' in rejiggered[gg] ):
                                                # Catch this switch thing, use the var name after / and set to True, it's a switch
                                                rejiggered_defaults.append(rejiggered[gg][rejiggered[gg].find('/')+1:]+' = True'); # Tack it on
                                            else:
                                                rejiggered_defaults.append(rejiggered[gg]); # Tack it on
                                            # END IF
                                        # END IF
                                    # END FOR gg
                                    if( FLG_forceFun == r',' ):
                                        if( idl[jk].find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                            idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                            if( len(rejiggered_defaults) > 0 ):
                                                idl[jk] += ', '+', '.join(rejiggered_defaults)+' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                            else:
                                                idl[jk] += ' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                            # END IF
                                        else:
                                            idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                            if( len(rejiggered_defaults) > 0 ):
                                                idl[jk] += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                            else:
                                                idl[jk] += ' )'; # Badabing, badaboom
                                            # END IF
                                        # END IF
                                        if( len(rejiggered_outs) == 0 ):
                                            regexr_emptyEq = regex_avoid(r'^\s*= *', idl[jk], skipums);
                                            if( regexr_emptyEq is not None ):
                                                idl[jk] = strreplace(idl[jk], regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                            # END IF
                                        # END IF
                                    else:
                                        # This was called as a function so check for an ='s and if it's there don't bother
                                        if( idl[jk].find('=') > -1 ):
                                            paren_match = parenthesis_hunter(idl[jk][regexr_fun.start():])+regexr_fun.start();
                                            bit_inside = idl[jk][regexr_fun.end():paren_match].split(',');
                                            for jj in range(0, len(bit_inside)):
                                                bit_inside[jj] = bit_inside[jj].strip(' ');
                                                if( bit_inside[jj][0] == '/' ):
                                                    bit_inside[jj] = bit_inside[jj][1:]+' = True'; # Make it better
                                                # END IF
                                            # END FOR jj
                                            bit_inside = ', '.join(bit_inside); # REBUILD
                                            idl[jk] = strreplace(idl[jk], regexr_fun.end(), paren_match, bit_inside)
                                        else:
                                            if( idl[jk].find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                                idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                                if( len(rejiggered_defaults) > 0 ):
                                                    idl[jk] += ', '+', '.join(rejiggered_defaults)+' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                                else:
                                                    idl[jk] += ' ) '+idl[jk][idl[jk].find(';'):]; # Badabing, badaboom
                                                # END IF
                                            else:
                                                idl[jk] = idl[jk][:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                                if( len(rejiggered_defaults) > 0 ):
                                                    idl[jk] += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                                else:
                                                    idl[jk] += ' )'; # Badabing, badaboom
                                                # END IF
                                            # END IF
                                            if( len(rejiggered_outs) == 0 ):
                                                regexr_emptyEq = regex_avoid(r'^\s*= *', idl[jk], skipums);
                                                if( regexr_emptyEq is not None ):
                                                    idl[jk] = strreplace(idl[jk], regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                                # END IF
                                            # END IF
                                        # END IF
                                    # END IF
                                    
                                    print('--- DONE WITH '+finds[0]+' ---\n');
                                    
                                    FLG_used = True; # It was used!
                                else:
                                    print('WARNING: "'+funName+'.pro" was not found in the libs!');
                                    print('Line in question: \n'+idl[jk]);
                                    print('Ignoring. Find it and this incantation will transform it too!\n');
                                # END IF
                            elif( (regexr_fun_avoidRecurse == True ) or (False) ):
                                # Since can't analyse, return all things that went in - future may need to parse the IDL function comments
                                regexr_comment = regex_avoid(r' *;', idl[jk], None); # Regex it
                                if( regexr_comment is None ):
                                    endy = ''; # Nothing to end with
                                    endy_indx = len(idl[jk]); # End is the end
                                else:
                                    endy = idl[jk][regexr_comment.start():]; # The endy call
                                    endy_indx = regexr_comment.start(); # End is the comment start
                                    # bevItUp = strreplace(bevItUp, regexr_comment.start(), len(bevItUp), ''); # Yeet the comment
                                # END IF
                                
                                reals = splitterz(idl[jk][regexr_fun.end():endy_indx], ',', splitums+[['(',')']]); # Get the inputs
                                eq_ops = [];
                                slash_ops = [];
                                for jj in range(len(reals)-1, -1, -1):
                                    if( '=' in reals[jj] ):
                                        eq_ops.append(reals[jj].strip(' ')); # Record
                                        reals.pop(jj); # Yeet
                                    elif( '/' == reals[jj].strip(' ')[0] ):
                                        slash_ops.append(reals[jj].strip(' ')); # Record
                                        reals.pop(jj); # Yeet
                                    else:
                                        reals[jj] = reals[jj].strip(' '); # Remove spaces just in case
                                    # END IF
                                # END FOR jj
                                if( len(slash_ops) > 0 ): # Didn't work this one out, should be fast at least sorry future me
                                    breakpoint()
                                    pass
                                # END IF
                                reals_out = reals.copy(); # out doesn't need numbers
                                for jj in range(len(reals_out)-1, -1, -1):
                                    if( reals_out[jj][0].isnumeric() ): # Assume variables can't start with a number
                                       reals_out.pop(jj); # Yeet
                                   # END IF
                                # END FOR jj
                                
                                # Rehydrate
                                idl[jk] = ', '.join(reals_out)+' = '+funName+'( '+', '.join(reals + eq_ops + slash_ops)+' )'+endy; # Rebuild but better
                            # END IF
                        # END IF
                        
                    # END FOR jk
                    if( FLG_used == False ):
                        defy_unused.append(defy_ins[j]); # It wasn't used
                    # END IF
                # END IF
            # END FOR j
            
            # Note the original mixed input/output as in, default, out, or unused
            defy_report = [None for _ in defy_ins]; # Prep
            for j in range(0, len(defy_ins)):
                if( defy_ins[j].find('=') > -1 ):
                    # Default
                    defy_report[j] = 'default;'+defy_ins[j][:defy_ins[j].find('=')]; # set default, record the var name - cause that is important
                elif( defy_ins[j] in defy_outs ):
                    # Output
                    defy_report[j] = 'output';
                elif( defy_ins[j] in defy_unused ):
                    # Unused
                    defy_report[j] = 'unused';
                else:
                    # Input
                    defy_report[j] = 'input';
                # END IF
            # END FOR j
            convertedCache_local[funName_now] = {'report':defy_report}; # Cache it for later, only need this thing to convert a function
            
            # Rename protected variable names
            for j in range(0, len(defy_ins)):
                if( defy_ins[j].find('=') > -1 ):
                    var2check = defy_ins[j][:defy_ins[j].find('=')].strip(' ').lower(); # Get only the var not the eq
                else:
                    var2check = defy_ins[j].lower(); # Good to go
                # END IF
                if( var2check in proctedPy_lower ): # We will be back if someone uses the variable "False" I think, or "None"
                    newbie = var2check+'y' ; # Make it not that
                    for jk in range(i+1, fend): # Go through every line and change it
                        fixr = 0; # Prep the fixr
                        regexr_varCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r'(?:['+straddlersR+r']|$)', idl[jk].lower(), skipums, stepUp = fixr);
                        while( regexr_varCheck is not None ):
                            # if( regexr_varCheck.start() != 0 ):
                            if( idl[jk][regexr_varCheck.start()] in straddlersR ):
                                sharty = regexr_varCheck.start()+1; # Remove one
                            else:
                                sharty = regexr_varCheck.start(); # Keep cause it's the start
                            # END IF
                            # if( regexr_varCheck.end() != len(idl[jk]) ):
                            if( idl[jk][regexr_varCheck.end()-1] in straddlersR ):
                                endy = regexr_varCheck.end()-1; # Remove one
                            else:
                                endy = regexr_varCheck.end(); # Keep cause it's the end
                            # END IF
                            
                            regexr_commaCheck= regex_avoid(r'(?:^\s*|else *|then *)'+var2check+r' *,', idl[jk].lower(), skipums, stepUp = fixr); # Comma stuff gotta start the line, I think
                            regexr_parenCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r' *\(', idl[jk].lower(), skipums, stepUp = fixr);
                            inParenCheck = where_enclosed_parenthesis(idl[jk], sharty, endy); # Check if in parentheses
                            
                            FLG_noIssue = True; # Good to go by default
                            if( regexr_commaCheck is not None ): # A lot of pomp and circumstance because it can NONE
                                FLG_noIssue = False; # There's an issue
                            # END IF
                            if( regexr_parenCheck is not None ):
                                if( regexr_varCheck.start() == regexr_parenCheck.start() ): # Could match a later one, prevent
                                    FLG_noIssue = False; # There's an issue
                                # END IF
                            # END IF
                            if( inParenCheck is not None ):
                                FLG_noIssue = True; # All good lol
                            # END IF
                            if( FLG_noIssue == True ):
                                idl[jk] = strreplace(idl[jk], sharty, endy, newbie); # Make it not var2check
                            # END IF
                            
                            fixr = regexr_varCheck.end(); # Move it up past this one
                            regexr_varCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r'(?:['+straddlersR+r']|$)', idl[jk].lower(), skipums, stepUp = fixr);
                        # END WHILE
                    # END FOR jk
                    
                    # Time for a big old switcherooo
                    defy_ins[j] = defy_ins[j].replace(var2check, newbie); # Switcheroo
                    regexr = regex_avoid(var2check+r' *[,=]', bevItUp.lower(), skipums);
                    if( bevItUp[regexr.end()-1] == '=' ): # Replace defy_ins[j] in bevItUp
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), newbie+' ='); # Replace the var name, carefully
                    else:
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), newbie+','); # Replace the var name, carefully
                    # END IF
                    for j in range(0, len(defy_outs)):
                        if( defy_outs[j].find('=') > -1 ):
                            var2check2 = defy_outs[j][:defy_outs[j].find('=')].strip(' ').lower(); # Get only the var not the eq
                        else:
                            var2check2 = defy_outs[j].lower(); # Good to go
                        # END IF
                        if( var2check == var2check2 ):
                            defy_outs[j] = defy_outs[j].replace(var2check2, newbie); # Switcheroo
                        # END IF
                    # END FOR j
                    for j in range(0, len(defy_unused)):
                        if( defy_unused[j].find('=') > -1 ):
                            var2check2 = defy_unused[j][:defy_unused[j].find('=')].strip(' ').lower(); # Get only the var not the eq
                        else:
                            var2check2 = defy_unused[j].lower(); # Good to go
                        # END IF
                        if( var2check == var2check2 ):
                            defy_unused[j] = defy_unused[j].replace(var2check2, newbie); # Switcheroo
                        # END IF
                    # END FOR j
                # END IF
            # END FOR j
            
            # Rebuild the def, but better
            for j in range(0, len(defy_outs)):
                regexr = regex_avoid(r' *'+defy_outs[j]+r' *(?:,|\)|= *\w+,|= *\w+\))', bevItUp, skipums);
                if( bevItUp[regexr.end()-1] == ')' ):
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end()-1, ''); # Delete the outs, carefully
                else:
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), ''); # Delete the outs, carefully
                # END IF
            # END FOR j
            for j in range(0, len(defy_unused)):
                regexr = regex_avoid(r' *'+defy_unused[j]+r' *(?:,|\)|= *\w+,|= *\w+\))', bevItUp, skipums);
                if( bevItUp[regexr.end()-1] == ')' ):
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end()-1, ''); # Delete the unused, carefully
                else:
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), ''); # Delete the unused, carefully
                # END IF
            # END FOR j
            # Find a comment
            commenty = bevItUp.find(';'); # Find a comment in the line
            # Clean up commas
            if( commenty > -1 ):
                bevItUp = bevItUp[:commenty].replace(' ','').replace('\t','')+bevItUp[commenty:]; # No spaces, it helps with the fixed-width lookbehind requirement
                commenty = bevItUp.find(';'); # Find a comment in the line again, cause it moved
            else:
                bevItUp = bevItUp.replace(' ','').replace('\t',''); # No spaces, it helps with the fixed-width lookbehind requirement
            # END IF
            regexr = regex_avoid(r'((?<!\w), *, *,)+|((?<!\w), *,)+', bevItUp, skipums);
            while( regexr is not None ):
                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Yeet the double/triple commas
                regexr = regex_avoid(r'((?<!\w), *, *,)+|((?<!\w), *,)+', bevItUp, skipums);
            # END WHILE
            # Deal with line splits
            if( commenty > -1 ):
                bevItUp = strinsert(bevItUp, commenty, ': ');
            else:
                bevItUp = bevItUp+':'; # Tack on the :
            # END IF
            # Rehydrate
            regexr_defy = regex_avoid(r'^\s*def.', bevItUp, skipums); # Regex it
            bevItUp = strreplace(bevItUp, regexr_defy.start(), regexr_defy.end(), 'def '); # The . kept def from running into the function name
            bevItUp = bevItUp.replace(',)',')').replace(',',', ').replace('(','( ').replace(')',' )').replace('=',' = '); # Avoid ,) situation then fix spacing
            regexr = regex_avoid(r', *\)', bevItUp, skipums_py); # Start of function definition
            if( regexr is not None ):
                bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), ')'); # Catch empty stuff, shoulda caught before but whatever
            # END IF
            FLG_spacer = 1; # Move everything up after this
            bevItUp = bevItUp.split('$\n'); # yee split the lines
            if( len(bevItUp) > 1 ):
                bevItUp[0] += ' \\'; # Tack on the backslash
                for jk in range(1, len(bevItUp)):
                    bevItUp[jk] = (spacer+4)*' '+bevItUp[jk].lstrip(' '); # New line gets some spaces so it looks better
                    if( jk != (len(bevItUp)-1) ):
                        bevItUp[jk] += ' \\'; # Tack on the backslash
                    # END IF
                # END FOR jk
            # END IF
            # Scan for n_params() because it's zesty
            for jk in range(i+1, fend):
                regexr = regex_avoid(r'n_params\( *\)', idl[jk].lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_eq1 = regex_avoid(r'n_params\( *\) *eq *\d+', idl[jk].lower(), skipums); # Regex it
                    if( regexr_eq1 is not None ):
                        # Semi-solution here is to make a new function input for "want output" named FLG_wantOutput = True
                        if( 'FLG_wantOutput = True' not in bevItUp[-1] ):
                            bevItUp[-1] = strinsert(bevItUp[-1], bevItUp[-1].rfind(' ):'), ', FLG_wantOutput = True');
                        # END IF
                        idl[jk] = strreplace(idl[jk], regexr_eq1.start(), regexr_eq1.end(), 'FLG_wantOutput eq False'); # Replace
                    else:
                        pass
                        # print('WARNING: Unsupported use of "n_params()" on IDL line '+str(jk)+', printing line:\n'+idl[jk]);
                        # breakpoint();
                        idl[jk] = strreplace(idl[jk], regexr.start(), regexr.end(), '( False == True )'); # Replace with something that will never activate
                    # END IF
                    
                    regexr = regex_avoid(r'n_params\( *\)', idl[jk].lower(), skipums); # Regex it
                # END WHILE
            # END FOR jk
            
            # Set the outs at all returns (there can be manyyy!)
            if( len(defy_outs) > 0 ):
                
                # Insert outs into all returns, cause idl lacks that cause you know
                for jk in range(i+1, fend):
                    # searchr_isin_where = strisin_where( idl[jk].lower(), 'return', straddlers );
                    # if( (len(searchr_isin_where) > 0) and avoider( idl[jk][:searchr_isin_where[0]], skipums ) ): # See if in it
                    searchr_isin = regex_avoid_logic(r'^\s*return( |,|$)', idl[jk].lower(), skipums);
                    if( searchr_isin == True ): # See if in it
                        searchr_isin_where = strisin_where( idl[jk].lower(), 'return', straddlers );
                        outz_strang = ' '; # Build it
                        for outz in defy_outs: # Roll through all outs
                            FLG_declared = False; # Determine if it was declared
                            for kj in range(jk-1, i, -1):
                                searchr_isin_where_outz = strisin_where( idl[kj].replace(' ',''), outz+'=', straddlers );
                                if( (len(searchr_isin_where_outz) > 0) and avoider( idl[kj][:searchr_isin_where_outz[0]], skipums ) ): # See if in it
                                    FLG_declared = True;
                                # END IF
                            # END FOR kj
                            if( FLG_declared ):
                                outz_strang += outz+', '; # Tack it on
                            else:
                                outz_strang += 'None, '; # Tack on None b/c not declared
                            # END IF
                        # END FOR outz
                        idl[jk] = strreplace( idl[jk], searchr_isin_where[1], searchr_isin_where[1], outz_strang.rstrip(', ') ); # Insert
                    # END IF
                # END FOR jk
            # END IF
            
            # --- Standardize the bevItUp to a list ---
            if( not isinstance(bevItUp, list) ): # After this bevItUp is always a list, makes it easier to target
                bevItUp = [bevItUp]; # Love it or list it
            # END IF
           
        #!!!
        # --- Everything that's not a pro/function definition (less divination requried) --- 
        else:
            codez4later = []; # Prime it up
            FLG_realsies = True; # Prime it up
            # Empty line - find it to quit it
            if( bevItUp == '' ):
                FLG_realsies = False; # Taken care of later, but no need to ponder it
            # Comment line - find it to quit it
            elif( start_finder( bevItUp.replace('\t','').replace(' ',''), ';' ) ):
                FLG_realsies = False; # Taken care of later, but no need to ponder it
            # END IF
            
            if( FLG_realsies ):               
                
                # Look for illegal names that are python functions (sum, ^, 0b, 1b, ||, &&)
                regexr = regex_avoid(r'[\s*\(+-/*=,]sum[ +-/*,=\)]', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].lower().find('sum') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 3; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'sumz' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'[\s*\(+-/*=,]sum[ +-/*,=\)]', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'\^', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('^') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 1; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, '**' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'\^', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r' AND ', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' and ' ); # Replace the bit!
                    
                    regexr = regex_avoid(r' AND ', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r' OR ', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' or ' ); # Replace the bit!
                    
                    regexr = regex_avoid(r' OR ', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'\|\|', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('||') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    repStr = 'or'; # Build it
                    if( bevItUp[perfRep_start-1] != ' ' ):
                        repStr = ' '+repStr; # Add it on
                    # END IF
                    if( bevItUp[perfRep_end] != ' ' ):
                        repStr += ' '; # Add it on
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, repStr ); # Replace the bit!
                    
                    regexr = regex_avoid(r'\|\|', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'&&', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('&&') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    repStr = 'and'; # Build it
                    if( bevItUp[perfRep_start-1] != ' ' ):
                        repStr = ' '+repStr; # Add it on
                    # END IF
                    if( bevItUp[perfRep_end] != ' ' ):
                        repStr += ' '; # Add it on
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, repStr ); # Replace the bit!
                    
                    regexr = regex_avoid(r'&&', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'[\(,\s+]0b[, *\)]*', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].lower().find('0b') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'False' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'[\(,\s+]0b[, *\)]*', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'[\(,\s+]1b[, *\)]*', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].lower().find('1b') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'True' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'[\(,\s+]1b[, *\)]*', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+b(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+b', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.uint8( '+bevItUp[perfRep_start:perfRep_end-1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+b(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+s(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+s', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.int16( '+bevItUp[perfRep_start:perfRep_end-1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+s(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+us(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+us', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.uint16( '+bevItUp[perfRep_start:perfRep_end-2]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+us(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+u(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+u', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.uint16( '+bevItUp[perfRep_start:perfRep_end-1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+u(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ll(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+ll', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.int64( '+bevItUp[perfRep_start:perfRep_end-2]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ll(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ull(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+ull', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.uint64( '+bevItUp[perfRep_start:perfRep_end-3]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ull(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+l(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+l', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.int32( '+bevItUp[perfRep_start:perfRep_end-1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+l(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ul(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+ul', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.uint32( '+bevItUp[perfRep_start:perfRep_end-2]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+ul(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+\.*\d*d(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+\.*\d*d', bevItUp[regexr.start():regexr.end()].lower(), skipums); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == (regexr.end()-regexr.start()) ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, 'np.float64( '+bevItUp[perfRep_start:perfRep_end-1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+\.*\d*d(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+\.d\d+(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_heck = regex_avoid(r'\d+\.d\d+', bevItUp[:regexr.end()].lower(), skipums, stepUp=regexr.start() ); # Regex it
                    if( regexr_heck.start() == 1 ):
                        perfRep_start = regexr.start()+1; # Get the perfect replacement going
                    else:
                        perfRep_start = regexr.start(); # Get the perfect replacement going
                    # END IF
                    if( regexr_heck.end() == regexr.end() ):
                        perfRep_end = regexr.end(); # Get the perfect replacement going
                    else:
                        perfRep_end = regexr.end()-1; # Get the perfect replacement going
                    # END IF
                    replacer = bevItUp[perfRep_start:perfRep_end];
                    replacer = bevItUp[perfRep_start:perfRep_end].lower().split('.d'); # Time to get to work figuring out this stupid stuff
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, ' np.float64( '+replacer[0]+'*10**'+replacer[1]+' )' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(?:['+straddlersR+r']|^)\d+\.d\d+(?:['+straddlersR+r']|$)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'\w+ *--', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('--') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, ' -= 1' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'\w+ *--', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'\w+ *\+\+', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('++') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + 2; # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, ' += 1' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'\w+ *\+\+', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'\[ *\* *\]', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    perfRep_start = bevItUp[regexr.start():regexr.end()].find('[') + regexr.start(); # Get the perfect replacement going
                    perfRep_end = perfRep_start + regexr.end() - regexr.start(); # Add on length of thing want to replace
                    bevItUp = strreplace( bevItUp, perfRep_start, perfRep_end, '[:]' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'\w+ *\+\+', bevItUp, skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'!values.d_nan', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.nan' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'!values.d_nan', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'!pi', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.pi' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'!pi', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'!dpi', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.pi' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'!dpi', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                regexr = regex_avoid(r'!radeg', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '180/np.pi' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'!radeg', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                   
                # if( 'lonpole NE 1.8d2' in bevItUp ):
                #     breakpoint()
                #     pass
                
                # Case Catcher
                if( FLG_case == False ):
                    # Case statement - get into it (only need to get into it if case is off)
                    regexr = regex_avoid(r'^\s*case +.+ +of', bevItUp.lower(), skipums); # Regex it
                    if( regexr is not None ):
                        # Case becomes if statement
                        regexr_case = regex_avoid(r'case +.+ +of', bevItUp.lower(), skipums); # Regex it
                        repl = bevItUp[regexr_case.start()+4:regexr_case.end()-2].strip(' ');
                        
                        if( repl == '1' ):
                            FLG_case_accursedIf = 1; # It's accursed if time!
                        else:
                            FLG_case_var = repl; # Record this
                            # bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Wipe out the case statement, it's worthless
                            # print('Case statement with actual case action, ponder how to implement.')
                            # breakpoint() # Ponder this
                        # END IF
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Wipe out the case statement, it's worthless
                        FLG_case = 1; # Fire these up
                        FLG_lastOpen.append('case');
                    # END IF
                else:
                    # Extra scrutiny if case is on
                    # endcase statement - get into it
                    regexr = regex_avoid(r'^\s*endcase', bevItUp.lower(), skipums); # Regex it
                    if( regexr is not None ):
                        bevItUp = '# END IF'+bevItUp[regexr.end():]; # Simple!
                        spacer -= 4; # Move everything back NOW
                        FLG_case = False; # End these
                        FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('case') - 1); # Remove from here as well
                        FLG_case_accursedIf = False;
                        # FLG_case_thenWithNoBegin = False;
                        # if( FLG_caseClosed == False ):
                        #     # Closes the open if statement if it wasn't closed by an else call
                        #     FLG_IF_open -= 1; # Nice
                        #     FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('if') - 1); # Remove from here as well
                        # else:
                        #     FLG_caseClosed = False; # Turn it off
                        # # END IF
                        FLG_caseIf = False; # No case if
                    else:
                        # This is for every line during a case statement zone
                        if( FLG_case_accursedIf > 0 ):
                            regexr_caseElse = regex_avoid( r'^\s*else *:', bevItUp, skipums); # Catch a case
                            regexr_case = regex_avoid( r'^\s*[\w ,+\-*/^<>[\]()&|]+ *:', bevItUp, skipums); # Catch a case
                            if( regexr_caseElse is not None ):
                                # Special ending case!
                                if( regexr_caseElse.end() == len(bevItUp) ):
                                    # Special-special case of empty case! woowwwwwwww
                                    bevItUp = 'else then pass'; # Woo
                                else:
                                    if( regexr_caseElse.end()+1 < len(bevItUp) ):
                                        endy = ' '+bevItUp[regexr_caseElse.end()+1:]; # Tack on the test if it exists
                                    else:
                                        endy = ''; # Nothin
                                    # END IF
                                    bevItUp = 'else then'+endy; # Slam it
                                # END IF
                                FLG_caseIf = True; # It's a case if
                            elif ( regexr_case is not None ):
                                if( regexr_case.end()+1 < len(bevItUp) ):
                                    endy = ' '+bevItUp[regexr_case.end():]; # Tack on the test if it exists
                                else:
                                    endy = ''; # Nothin
                                # END IF
                                if( FLG_case_accursedIf == 1 ):
                                    bevItUp = 'if ( '+bevItUp[regexr_case.start():regexr_case.end()-1]+' ) then'+endy; # Make it an if statement
                                else:
                                    bevItUp = 'endif else if ( '+bevItUp[regexr_case.start():regexr_case.end()-1]+' ) then'+endy; # Make it an if statement
                                # END IF
                                if( not regex_avoid_logic(r'^\s*begin', endy.lower(), skipums)  ):
                                    # FLG_case_thenWithNoBegin = True;
                                    if( bevItUp.strip(' ')[-4:] == 'then' ):
                                        # Special case of empty case! woowwwwwwww
                                        bevItUp += ' pass'; # Woo
                                    # END IF
                                # END IF
                                FLG_case_accursedIf += 1; # Increment, so know moved off of if
                                FLG_caseIf = True; # It's a case if
                            else:
                                FLG_caseIf = False; # No case if
                            # END IF
                        else:
                            regexr_caseElse = regex_avoid( r'^\s*else *:', bevItUp.lower(), skipums); # Catch a case
                            regexr_case = regex_avoid( r"^\s*[\w ,+\-*/^<>'[\]()&|]+ *:", bevItUp, skipums); # Catch a case
                            if( regexr_caseElse is not None ):
                                # Special ending case!
                                if( regexr_caseElse.end() == len(bevItUp) ):
                                    # Special-special case of empty case! woowwwwwwww
                                    bevItUp = 'else then pass'; # Woo
                                else:
                                    if( regexr_caseElse.end()+1 < len(bevItUp) ):
                                        endy = ' '+bevItUp[regexr_caseElse.end()+1:]; # Tack on the test if it exists
                                    else:
                                        endy = ''; # Nothin
                                    # END IF
                                    bevItUp = 'else then'+endy; # Slam it
                                # END IF
                                FLG_caseIf = True; # It's a case if
                            elif ( regexr_case is not None ):
                                if( regexr_case.end()+1 < len(bevItUp) ):
                                    endy = ' '+bevItUp[regexr_case.end():]; # Tack on the test if it exists
                                else:
                                    endy = ''; # Nothin
                                # END IF
                                if( FLG_case == 1 ):
                                    bevItUp = 'if ( '+FLG_case_var+' == '+bevItUp[regexr_case.start():regexr_case.end()-1].strip(' ')+' ) then'+endy; # Make it an if statement
                                else:
                                    bevItUp = 'endif else if ( '+FLG_case_var+' == '+bevItUp[regexr_case.start():regexr_case.end()-1].strip(' ')+' ) then'+endy; # Make it an if statement
                                # END IF
                                if( not regex_avoid_logic(r'^\s*begin', endy.lower(), skipums) ):
                                    # FLG_case_thenWithNoBegin = True;
                                    if( bevItUp.strip(' ')[-4:] == 'then' ):
                                        # Special case of empty case! woowwwwwwww
                                        bevItUp += ' pass'; # Woo
                                    # END IF
                                # END IF
                                FLG_case += 1; # Increment, so know if moved off of if
                                FLG_caseIf = True; # It's a case if
                            else:
                                FLG_caseIf = False; # No case if
                            # END IF
                        # END IF
                    # END IF
                # END IF
                                
                # patch for "END" being able to END IF STATEMENTS not just ENDIF, consistency?? NONE; one thousand curses upon the language designers
                regexrL = regex_avoid_logic(r'^\s*(?:end[ ;]|end$)', bevItUp.lower(), skipums) and strisin( bevItUp.lstrip('\t').lstrip(' ').lower(), 'end', straddlers ); # Regex it
                if( regexrL and ((FLG_IF_open > 0) or (FLG_ELSE_open > 0) or (FLG_case > 0) or (FLG_FOR_open > 0)) ):
                    regexr = regex_avoid(r'(\s*end\s*)', bevItUp.lower(), skipums); # Regex it
                    if( len(FLG_lastOpen) == 0 ):
                        if( FLG_IF_open > 0 ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endif' ); # Replace the bit!
                        elif ( FLG_ELSE_open > 0 ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endelse' ); # Replace the bit!
                        elif ( FLG_case > 0 ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Wipe it out, unnecessary
                        elif ( FLG_FOR_open > 0 ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endfor' ); # Replace the bit!
                        # END IF
                    else:
                        if( (FLG_lastOpen[-1] == 'if') and (FLG_IF_open > 0) ):
                            if( (FLG_case > 0) and (FLG_caseIf == False) ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Replace the bit!
                            else:
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endif' ); # Replace the bit!
                            # END IF
                        elif( (FLG_lastOpen[-1] == 'else') and (FLG_ELSE_open > 0) ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endelse' ); # Replace the bit!
                        elif( (FLG_lastOpen[-1] == 'case') and (FLG_case > 0) ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Replace the bit!
                        elif( (FLG_lastOpen[-1] == 'for') and (FLG_FOR_open > 0) ):
                            bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endfor' ); # Replace the bit!
                        else:
                            print('Unequal if/else/for counter!')
                            breakpoint()
                            if( FLG_IF_open > 0 ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endif' ); # Replace the bit!
                            elif ( FLG_ELSE_open > 0 ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endelse' ); # Replace the bit!
                            elif ( FLG_case > 0 ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '' ); # Wipe it out, unnecessary
                            elif ( FLG_FOR_open > 0 ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'endfor' ); # Replace the bit!
                            # END IF
                        # END IF
                        # FLG_lastOpen.pop(-1); # Ditch it
                    # END IF
                # END IF
                                
                # If statement - get into it
                # First deal with endif else if
                regexr = regex_avoid(r'^\s*endif *else[ \$\n]*if', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    # breakpoint()
                    FLG_elif = True; # Trigger
                    if( FLG_elifSplitLine == True ):
                        FLG_lastOpen.append('if'); # Undo some stuff
                        codez.pop(-1); # Remove the last line which is an # END IF, added b/c couldn't know ya know
                        FLG_elifSplitLine = False; # All good
                    else:
                        spacer -= 4; # Move everything back NOW
                    # END IF
                    regexr = regex_avoid(r'^\s*endif *else[ \$\n]*', bevItUp.lower(), skipums); # Regex it
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), ''); # Nix else so it's an if statement and the if statement can handle it
                else:
                    FLG_elif = False; # Reset
                    # if( FLG_elif == True ):
                    #     regexr_start = regex_avoid(r'^\s*endif *else', bevItUp.lower(), skipums); # Regex it
                    #     if( regexr_start is not None ):
                    #         breakpoint()
                    # else:
                    #     FLG_elif = False; # Reset
                    # # END IF
                # END IF
                # Then deal with else if mid-line
                if( FLG_IF_open > 0 ):
                    regexr = regex_avoid(r'else *if +', bevItUp.lower(), skipums); # Regex it
                    if( regexr is not None ):
                        regexr_start = regex_avoid(r'^\s*else *if', bevItUp.lower(), skipums); # Regex it
                        if( regexr_start is not None ):
                            FLG_elif = True; # Trigger
                            spacer -= 4; # Move everything back NOW
                            regexr = regex_avoid(r'^\s*else', bevItUp.lower(), skipums); # Regex it
                            bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), ''); # Nix else so it's an if statement and the if statement can handle it
                        else:
                            # Eject it so it can be dealt with later
                            FLG_elifSplitLine = True; # Yep it gets so weird
                            idl.insert(i+1, 'endif '+bevItUp[regexr.start():]); # Byeee
                            fend += 1; # More fend to cover
                            bevItUp = strreplace(bevItUp, regexr.start(), len(bevItUp), '').rstrip(' ').rstrip('$\n'); # Make it so it's a regular call
                        # END IF
                    # END IF
                # END IF
                # CHeck if "IF" starts the line - gotta
                regexr = regex_avoid(r'^\s*if', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' if' ); # Enforce lower-case if
                    regexr = regex_avoid(r'^\s*if\s*', bevItUp.lower(), skipums); # Regex it
                    regexr_ifMore = regex_avoid(r' +if +', bevItUp[regexr.end():].lower(), skipums); # Regex it
                    # Determine what kind of if we're working with
                    if( regexr_ifMore is None ):
                        regexr_thenBegin = regex_avoid(r'\s*then +begin\s*', bevItUp.lower(), skipums)
                        regexr_then = regex_avoid(r'\s+then\s+', bevItUp.lower(), skipums); # Ask for it for real
                        regexr_else = regex_avoid(r'\s+else\s+', bevItUp.lower(), skipums); # Ask for it for real
                        regexr_elseBegin = regex_avoid(r'\s+else +begin\s*', bevItUp.lower(), skipums); # Ask for it for real
                    else:
                        # If there are more ifs in this line, which can happen, limit the lookahead
                        regexr_thenBegin = regex_avoid(r'\s*then +begin\s*', bevItUp[:regexr.end()+regexr_ifMore.start()].lower(), skipums);
                        regexr_then = regex_avoid(r'\s+then(?:\s+|$)', bevItUp[:regexr.end()+regexr_ifMore.start()].lower(), skipums); # Ask for it for real
                        regexr_else = regex_avoid(r' +else(?:\s+|$)', bevItUp[:regexr.end()+regexr_ifMore.start()].lower(), skipums); # Ask for it for real
                        regexr_elseBegin = regex_avoid(r' +else +begin\s*', bevItUp[:regexr.end()+regexr_ifMore.start()].lower(), skipums); # Ask for it for real
                    # END IF
                    if( regexr_thenBegin is not None ):
                        # ez pz works right
                        if( regexr_thenBegin.end() == len(bevItUp) ):
                            bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ':' ); # Actual end, so no space
                        else:
                            bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ': ' ); # Comment or something after, so space
                        # END IF
                        FLG_spacer = 1; # Move it up for next time
                    elif( (regexr_then is not None) and (regexr_else is None) and (regexr_elseBegin is None) ):
                        regexr_holladolla = regex_avoid(r'^\s*\$(\s|\n)*\s*', bevItUp[regexr_then.end():].lower(), skipums);
                        regexr_holladollaCommy = regex_avoid(r'\$ *;.*\n', bevItUp[regexr_then.end():].lower(), skipums);
                        newLineCntr = 1; # Prep it
                        if( regexr_holladolla is not None ):
                            idl.insert(i+newLineCntr,bevItUp[regexr_then.end()+regexr_holladolla.end():]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        elif( regexr_holladollaCommy is not None ):
                            idl.insert(i+newLineCntr,bevItUp[regexr_then.end():(regexr_holladollaCommy.start()+regexr_then.end())]+'$\n'); # Split at "then", put it into IDL for later (basically making it a real if statement)
                            newLineCntr += 1; # Increment
                            idl.insert(i+newLineCntr,bevItUp[(regexr_holladollaCommy.end()+regexr_then.end()):]+\
                                       bevItUp[(regexr_holladollaCommy.start()+regexr_then.end()+1):(regexr_holladollaCommy.end()+regexr_then.end()-1)]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        else:
                            idl.insert(i+newLineCntr,bevItUp[regexr_then.end():]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        # END IF
                        bevItUp = bevItUp[:regexr_then.start()]+':'; # Remove the split bit, add a :
                        if( FLG_caseIf == False ): # Don't add an endif if it's a case statement thing
                            newLineCntr += 1; # Increment
                            idl.insert(i+newLineCntr,'endif'); # Tack one more to finish it off as a real big if statement - this is to deal with spaces better
                        # END IF
                        fend += newLineCntr; # More fend to cover
                        FLG_spacer = 1; # Move it up for next time
                    elif( (regexr_then is not None) and (regexr_elseBegin is not None) ):
                        idl.insert(i+1,bevItUp[regexr_then.end():regexr_else.start()].strip('$\n')); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        idl.insert(i+2,'else@'); # Tack on the else: manually
                        fend += 2; # More fend to cover
                        FLG_spacer = 1; # Move it up for next time
                        bevItUp = bevItUp[:regexr_then.start()]+':'; # Remove the split bit, add a :
                    elif( (regexr_then is not None) and (regexr_else is not None) ):
                        line2drop = bevItUp[regexr_then.end():regexr_else.start()].strip('$\n');
                        regexr_lostComment = regex_avoid(r'^\s*;', line2drop, skipums);
                        lostComment = ''; # Holding nothing usually
                        if( regexr_lostComment is not None ):
                            regexr_newLine = regex_avoid(r'^\s*;.*\n', line2drop, skipums);
                            lostComment = line2drop[:regexr_newLine.end()].strip('$\n'); # Catch that lost comment
                            line2drop = line2drop[regexr_newLine.end():]; # Trim off the comment
                        # END IF
                        idl.insert(i+1,line2drop.strip('$\n')); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        idl.insert(i+2,'else@'); # Tack on the else: manually
                        idl.insert(i+3,bevItUp[regexr_else.end():].strip('$\n')); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        idl.insert(i+4,'endelse'); # Tack one more to finish it off as a real big if statement - this is to deal with spaces better
                        fend += 4; # More fend to cover
                        FLG_spacer = 1; # Move it up for next time
                        bevItUp = bevItUp[:regexr_then.start()]+':'+lostComment; # Remove the split bit, add a :
                        if( FLG_elif == True ):
                            #!!!
                            FLG_IF_open -= 1; # Nice
                        # END IF
                    else:
                        print('Not supposed to if like this??');
                        breakpoint()
                        pass
                    # END IF
                    if( FLG_elif == True ):
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'elif ' ); # Make it an elif
                    else:
                        if( FLG_caseIf == False ):
                            FLG_IF_open += 1; # Great
                            FLG_lastOpen.append('if');
                            if( (regexr_then is not None) and (regexr_else is not None) ):
                                FLG_IF_open -= 1; # Nice
                                FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('if') - 1); # Remove from here as well
                            # END IF
                        # END IF
                    # END IF
                    
                    # Catch ~ which needs to become "not"
                    regexr = regex_avoid(r'(\s+~[a-zA-Z])', bevItUp, skipums); # Regex it
                    if( regexr is not None ):
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end()-1, ' not ' ); # Replace the bit!
                    # END IF
                # END IF

                # CHeck if "endif" starts the line - gotta
                regexrL = regex_avoid_logic(r'(^\s*endif *)', bevItUp.lower(), skipums); # Regex it #.lstrip('\t').lstrip(' ')
                if( regexrL == True ):
                    # Determine what kind of if we're working with
                    regexr_elseBegin = regex_avoid(r'else +begin', bevItUp.lower(), skipums)
                    regexr_else = regex_avoid(r' +else', bevItUp.lower(), skipums); # Ask for it for real
                    if( regexr_elseBegin is not None ):
                        bevItUp = 'else@'+bevItUp[regexr_elseBegin.end():]; # Simple!
                        FLG_spacer = 1; # Move it up for next time
                    elif( regexr_else is not None ):
                        # It's a long one
                        idl.insert(i+1,bevItUp[regexr_else.end():]); # Tack on next line manually
                        idl.insert(i+2,'endelse'); # End the else
                        fend += 2; # More fend to cover
                        bevItUp = 'else@'; # Only keep this for now, it'll trigger the next check
                    else:
                        spacer -= 4; # Move everything back NOW
                        regexr = regex_avoid(r'(\s*endif\s*)', bevItUp.lower(), skipums); # Regex it
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '; END IF' )
                    # END IF
                    FLG_IF_open -= 1; # Nice
                    FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('if') - 1); # Remove from here as well
                # END IF
                
                # Else statement - get into it
                # CHeck if "ELSE" starts the line - gotta
                regexrL = regex_avoid_logic(r'\s*else', bevItUp.lower(), skipums) and not regex_avoid_logic(r'endelse', bevItUp.lower(), skipums); # Regex it
                if( regexrL == True ): # If else is only ever used on a continued line, this can be simplified - not caring to find out now
                    # Determine what kind of else we're working with
                    regexr_elseAt = regex_avoid_logic(r'else@', bevItUp.lower(), skipums); # Already converted to Python style
                    if( regexr_elseAt  == True ):
                        spacer -= 4; # Move everything back NOW
                        FLG_spacer = 1; # Move it up for next time
                        FLG_ELSE_open += 1; # Great
                        FLG_lastOpen.append('else');
                    else:
                        regexr_else = regex_avoid(r'(^\s*else\s*)', bevItUp.lower(), skipums);
                        regexr_elseColon = regex_avoid(r'else *:', bevItUp.lower(), skipums); # Switch statement, ignore it
                        regexr_elseNewLine = regex_avoid(r'\$(.|\n)*else\s*', bevItUp.lower(), skipums);
                        if( regexr_elseColon is None ): # Don't do this on a switch statement else:
                            if( regexr_else is not None ):
                                spacer -= 4; # Move everything back NOW
                                regexr_thenBegin = regex_avoid(r'(\s+then begin\s*)', bevItUp.lower(), skipums)
                                regexr_then = regex_avoid(r'(\s+then\s+)', bevItUp.lower(), skipums); # Ask for it for real
                                if( regexr_thenBegin is not None ):
                                    # ez pz works right
                                    if( regexr_thenBegin.end() == len(bevItUp) ):
                                        bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ':' ); # Actual end, so no space
                                    else:
                                        bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ': ' ); # Comment or something after, so space
                                    # END IF
                                    FLG_spacer = 1; # Move it up for next time      
                                    if( FLG_caseIf == False ):
                                        FLG_ELSE_open += 1; # Great
                                        FLG_lastOpen.append('else');
                                    # END IF
                                elif( regexr_then is not None ):
                                    idl.insert(i+1,bevItUp[regexr_then.end():]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                                    bevItUp = bevItUp[:regexr_then.start()]+':'; # Remove the split bit, add a :
                                    if( FLG_caseIf == False ):
                                        idl.insert(i+2,'endelse'); # Tack one more to finish it off as a real big if statement - this is to deal with spaces better
                                        fend += 2; # More fend to cover
                                        FLG_ELSE_open += 1; # Great
                                        FLG_lastOpen.append('else');
                                    else:
                                        fend += 1; # More fend to cover
                                    # END IF
                                    FLG_spacer = 1; # Move it up for next time
                                else:
                                    breakpoint()
                                    pass
                                # END IF
                            elif( regexr_elseNewLine is not None ):
                                idl.insert(i+1,'else@'); # Tack on the else: manually
                                idl.insert(i+2,bevItUp[regexr_elseNewLine.end():]); # Get bit after the else
                                fend += 2; # More fend to cover
                                bevItUp = bevItUp[:regexr_elseNewLine.start()]; # reduce bevitup to just the first line
                                FLG_spacer = -1; # Move it back for next time (the else:)
                            else:
                                print('Not supposed to if like this??');
                                breakpoint()
                            # END IF
                            
                            regexr_thenBegin = regex_avoid(r'(\s+then begin\s*)', bevItUp.lower(), skipums)
                            regexr_then = regex_avoid(r'(\s+then\s+)', bevItUp.lower(), skipums); # Ask for it for real
                            if( regexr_thenBegin is not None ):
                                # ez pz works right
                                if( regexr_thenBegin.end() == len(bevItUp) ):
                                    bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ':' ); # Actual end, so no space
                                else:
                                    bevItUp = strreplace( bevItUp, regexr_thenBegin.start(), regexr_thenBegin.end(), ': ' ); # Comment or something after, so space
                                # END IF
                                FLG_spacer = 1; # Move it up for next time       
                                FLG_ELSE_open += 1; # Great
                                FLG_lastOpen.append('else');
                            elif( regexr_then is not None ):
                                idl.insert(i+1,bevItUp[regexr_then.end():]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                                bevItUp = bevItUp[:regexr_then.start()]+':'; # Remove the split bit, add a :
                                idl.insert(i+2,'endelse'); # Tack one more to finish it off as a real big if statement - this is to deal with spaces better
                                fend += 2; # More fend to cover
                                FLG_spacer = 1; # Move it up for next time
                                FLG_ELSE_open += 1; # Great
                                FLG_lastOpen.append('else');
                            # END IF
                            
                            # Catch ~ which needs to become "not"
                            regexr = regex_avoid(r'(\s+~\s*[a-zA-Z])', bevItUp, skipums); # Regex it
                            if( regexr is not None ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end()-1, ' not ' ); # Replace the bit!
                            # END IF
                        # END IF
                    # END IF
                # END IF
                
                # CHeck if "endelse" starts the line - gotta
                regexrL = regex_avoid_logic(r'^\s*endelse *', bevItUp.lower(), skipums); # Regex it
                if( regexrL == True ):
                    # EZ PZ it's donezo line
                    regexr = regex_avoid(r'(^\s*endelse)', bevItUp.lower(), skipums); # Regex it
                    bevItUp = '; END IF'+bevItUp[regexr.end():]; # Simple!
                    spacer -= 4; # Move everything back NOW
                    FLG_ELSE_open -= 1; # Nice
                    FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('else') - 1); # Remove from here as well
                    # FLG_IF_open -= 1; # Nice
                # END IF
                                
                # if statement shorthand ? hooboy
                regexr = regex_avoid(r'(\s+\?\s+)', bevItUp, skipums); # Regex it
                if( regexr is not None ):
                    # Slice n dice - get the "if" and the equals stuff
                    # FACTS: there must be an = sign
                    # One variable before = is assigned
                    # After = and before ? is if statement
                    # After ? and before : is "if then" line
                    # After : is "else" line
                    loc_q = bevItUp[regexr.start():regexr.end()].find('?') + regexr.start(); # Get exactly where it at
                    loc_eq = bevItUp.find('=');  # Don't need work, there left most = must be legit
                    regexr = regex_avoid(r'(\s+:\s+)', bevItUp, skipums); # Regex it
                    loc_col = bevItUp[regexr.start():regexr.end()].find(':') + regexr.start(); # Get exactly where it at
                    v_eq = bevItUp[:loc_eq+1]+' '; # Get the assignment variable, transposed over to upcomming lines
                    v_if = 'if( '+bevItUp[loc_eq+1:loc_q].strip(' ').lstrip('(').rstrip(')')+' ):'; # Get the if statement, build it
                    v_then = v_eq+bevItUp[loc_q+1:loc_col].strip(' '); # Get the if statement
                    v_else = v_eq+bevItUp[loc_col+1:].strip(' '); # Get the if statement
                    # update bev
                    bevItUp = v_if;
                    FLG_spacer = 1; # Move it up for next time
                    # Insert the lines as needed into idl to find later
                    idl.insert(i+1, v_then);
                    idl.insert(i+2, 'endif else begin'); # IDL-else
                    idl.insert(i+3, v_else);
                    idl.insert(i+4, 'endelse');
                    fend += 4; # More fend to cover
                    FLG_IF_open += 1; # Great
                    FLG_lastOpen.append('if');
                # END IF
                
                # For statement - get into it
                regexr = regex_avoid(r'^\s*for +', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_for = regex_avoid(r'^\s*for +(?:\w+|!\w+!) *= *[\w+\-\*/^\(\) \.\[\]]+ *, *[\w+\-\*/^\(\) \.\[\]]+ +do', bevItUp.lower(), skipums); # Regex it
                    regexr_forStepping = regex_avoid(r'^\s*for +(?:\w+|!\w+!) *= *[\w+\-\*/^\(\) \.\[\]]+ *, *[\w+\-\*/^\(\) \.\[\]]+, *[\w+\-\*/^\(\) \.\[\]]+ +do', bevItUp.lower(), skipums); # Regex it
                    if( regexr_forStepping is None ):
                        for_var = bevItUp[regexr.end():bevItUp.find('=')].strip(' '); # Get the var
                        for_min = bevItUp[bevItUp.find('=')+1:bevItUp.find(',')].strip(' '); # Get the value/var
                        for_max = bevItUp[bevItUp.find(',')+1:regexr_for.end()-3].strip(' '); # Get the value/var
                        regexr_for_begin = regex_avoid(r'^\s*for +(?:\w+|!\w+!) *= *[\w+\-\*/^\(\) \.\[\]]+ *, *[\w+\-\*/^\(\) \.\[\]]+ +do +begin', bevItUp.lower(), skipums); # Regex it
                        if( regexr_for_begin is not None ):
                            if( regexr_for_begin.end() == len(bevItUp) ):
                                endy = ''; # Nothing goin on
                            else:
                                endy = bevItUp[regexr_for_begin.end():]
                            # END IF
                            bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' + 1):'+endy; # Remake in our image
                        else:
                            # It's a one liner, deal with that
                            endy = bevItUp[regexr_for.end():]; # Assume do is not the end, safe bet
                            idl.insert(i+1, endy);
                            idl.insert(i+2, 'endfor');
                            fend += 2; # More fend to cover
                            bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' + 1):'; # Remake in our image
                        # END IF
                    else:
                        for_eq = bevItUp.find('='); # Get its loc
                        for_comma1 = bevItUp.find(','); # Get its loc
                        for_comma2 = bevItUp[for_comma1+1:].find(',')+for_comma1+1; # Get its loc
                        for_var = bevItUp[regexr.end():for_eq].strip(' '); # Get the var
                        for_min = bevItUp[for_eq+1:for_comma1].strip(' '); # Get the value/var
                        for_max = bevItUp[for_comma1+1:for_comma2].strip(' '); # Get the value/var
                        for_step = bevItUp[for_comma2+1:regexr_forStepping.end()-3].strip(' '); # Get the value/var
                        regexr_forStepping_begin = regex_avoid(r'^\s*for +(?:\w+|!\w+!) *= *[\w+\-\*/^\(\) \.\[\]]+ *, *[\w+\-\*/^\(\) \.\[\]]+, *[\w+\-\*/^\(\) \.\[\]]+ +do +begin', bevItUp.lower(), skipums); # Regex it
                        if( regexr_forStepping_begin is not None ):
                            if( regexr_forStepping_begin.end() == len(bevItUp) ):
                                endy = ''; # Nothing goin on
                            else:
                                endy = bevItUp[regexr_forStepping_begin.end():]
                            # END IF
                            if( for_step[0] == '-' ):
                                # Negative sign means count backwards, minor adjustment
                                bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' - 1, '+for_step+'):'+endy; # Remake in our image
                            else:
                                bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' + 1, '+for_step+'):'+endy; # Remake in our image
                            # END IF
                        else:
                            # It's a one liner, deal with that
                            endy = bevItUp[regexr_forStepping.end():]; # Assume do is not the end, safe bet
                            idl.insert(i+1, endy);
                            idl.insert(i+2, 'endfor');
                            fend += 2; # More fend to cover
                            if( for_step[0] == '-' ):
                                # Negative sign means count backwards, minor adjustment
                                bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' - 1, '+for_step+'):'; # Remake in our image
                            else:
                                bevItUp = 'for '+for_var+' in range('+for_min+', '+for_max+' + 1, '+for_step+'):'; # Remake in our image
                            # END IF
                        # END IF
                    # END IF
                    FLG_spacer = 1; # Move it up for next time
                    FLG_FOR_open += 1; # It's open
                    FLG_lastOpen.append('for');
                # END IF   
                
                # endfor statement - get into it
                regexr = regex_avoid(r'^\s*endfor', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = '# END FOR'+bevItUp[regexr.end():]; # Simple!
                    spacer -= 4; # Move everything back NOW
                    FLG_FOR_open -= 1; # It's closed
                    FLG_lastOpen.pop(len(FLG_lastOpen) - FLG_lastOpen[::-1].index('for') - 1); # Remove from here as well
                # END IF    
                
                # While statement - get into it
                regexr = regex_avoid(r'^\s*while *\(', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    matchin_parenthesis = parenthesis_hunter(bevItUp)+1; # Hunt where it happens
                    regexr = regex_avoid(r' +do +begin', bevItUp[matchin_parenthesis:].lower(), skipums); # Regex it
                    if( regexr is not None ):
                        bevItUp = strreplace( bevItUp, regexr.start()+matchin_parenthesis, regexr.end()+matchin_parenthesis, ':'); # Replace it
                    else:
                        regexr_do = regex_avoid(r' +do +', bevItUp[matchin_parenthesis:].lower(), skipums); # Regex it
                        idl.insert(i+1,bevItUp[regexr_do.end()+matchin_parenthesis:]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        bevItUp = strreplace( bevItUp, regexr_do.start()+matchin_parenthesis, len(bevItUp), ':'); # Replace it
                        idl.insert(i+2,'endwhile'); # Tack one more to finish it off as a real big if statement - this is to deal with spaces better
                        fend += 2; # More fend to cover
                        FLG_spacer = 1; # Move it up for next time
                    # END IF
                    FLG_spacer = 1; # Move it up for next time
                # END IF    
                
                # endwhile statement - get into it
                regexr = regex_avoid(r'^\s*endwhile', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = '# END WHILE'+bevItUp[regexr.end():]; # Simple!
                    spacer -= 4; # Move everything back NOW
                # END IF
                
                # Derpy REPEAT statement - get into it
                regexr = regex_avoid(r'^\s*repeat', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_begin = regex_avoid(r'^\s*repeat +begin', bevItUp.lower(), skipums); # Regex it
                    if( regexr_begin is not None ):
                        for j in range(i+1, fend):
                            regexr_until = regex_avoid(r'^\s*endrep +until', idl[j].lower(), skipums); # Regex it
                            if( regexr_until is not None ):
                                regexr_end = regex_avoid(r'^\s*endrep +until .+?(;|$)', idl[j].lower(), skipums); # Regex it
                                if( idl[j][regexr_end.end()-1] == ';' ):
                                    codez4later.append('FLG_runOnce = True'); # Ensure the while runs once, a requisite of "repeat"
                                    bevItUp = 'while( FLG_runOnce or '+idl[j][regexr_until.end():regexr_end.end()-1]+' ):'; # Create the while
                                    idl[j] = 'endwhile '+idl[j][regexr_end.end():]; # Call it a day there
                                else:
                                    codez4later.append('FLG_runOnce = True'); # Ensure the while runs once, a requisite of "repeat"
                                    bevItUp = 'while( FLG_runOnce or '+idl[j][regexr_until.end():]+' ):'; # Create the while
                                    idl[j] = 'endwhile'; # Call it a day there
                                # END IF
                                idl.insert(j, 'FLG_runOnce = False'); # End the FLG_runOnce
                                fend += 1; # More fend to cover
                                break;
                            # END IF
                        # END FOR j
                    else:
                        # Single line repeat (I guessed on this completely, sorry future me)
                        regexr_until = regex_avoid(r'^\s*repeat [\s\S]+ until', bevItUp.lower(), skipums); # Regex it
                        regexr_thing2calc_dollaHolla = regex_avoid(r'repeat [\s\S]+\$\n', bevItUp[regexr_until.start():regexr_until.end()].lower(), skipums); # Regex it
                        regexr_thing2calc_until = regex_avoid(r'repeat [\s\S]+until', bevItUp[regexr_until.start():regexr_until.end()].lower(), skipums); # Regex it
                        if( regexr_thing2calc_dollaHolla is not None): # I couldn't figure out how to combine them
                            if( regexr_thing2calc_dollaHolla.end() < regexr_thing2calc_until.end() ):
                                thing2calc = bevItUp[regexr_thing2calc_dollaHolla.start()+regexr_until.start()+6:regexr_thing2calc_dollaHolla.end()+regexr_until.start()-2].strip('\t').strip(' '); # Get just what we want
                            else:
                                thing2calc = bevItUp[regexr_thing2calc_until.start()+regexr_until.start()+6:regexr_thing2calc_until.end()+regexr_until.start()-5].strip('\t').strip(' '); # Get just what we want
                            # END IF
                        else:
                            thing2calc = bevItUp[regexr_thing2calc_until.start()+regexr_until.start()+6:regexr_thing2calc_until.end()+regexr_until.start()-5].strip('\t').strip(' '); # Get just what we want
                        # END IF
                        
                        idl.insert(i+1, thing2calc);
                        idl.insert(i+2, 'endwhile');
                        fend += 2; # More fend to cover
                        
                        regexr_end = regex_avoid(r'^\s*repeat [\s\S]+ until .+?(?:;|$)', bevItUp.lower(), skipums); # Regex it
                        if( bevItUp[regexr_end.end()-1] == ';' ):
                            bevItUp = 'while( '+bevItUp[regexr_until.end():regexr_end.end()-1].strip(' ')+' ): '+bevItUp[regexr_end.end():]; # Create the while
                        else:
                            bevItUp = 'while( '+bevItUp[regexr_until.end():].strip(' ')+' ):'; # Create the while
                        # END IF
                    # END IF
                    FLG_spacer = 1; # Move it up for next time
                # END IF 
                
                # Accursed goto statement, becomes while/if/manual refactor - get into it
                regexrL = regex_avoid_logic(r'^\s*\w+\s*:', bevItUp.lower(), skipums) and \
                    not regex_avoid_logic(r'^\s*else\s*:', bevItUp.lower(), skipums); # Regex it
                if( regexrL == True ):
                    regexr = regex_avoid(r'^\s*\w+\s*:', bevItUp.lower(), skipums); # Regex it
                    # This one needs a major rebuild because it's cursed
                    trigWord = bevItUp[regexr.start():-1].strip('\t').strip(' '); # Get the variable that it uses
                    FLG_goto = 0; # Note if found GOTO
                    goto_lineNum = [];
                    for j in range(i+1, fend):
                        regexr_goto = regex_avoid(r'(goto|GOTO) *, *'+trigWord, idl[j], skipums); # Regex it
                        if( regexr_goto is not None ):
                            FLG_goto += 1; # Increment
                            goto_lineNum.append(j);
                        # END IF
                    # END FOR j
                    if( FLG_goto == 1 ):
                        goto_lineNum = goto_lineNum[0]; # Just one by being here
                        regexr_if = regex_avoid(r'^\s*if +\w+ +then +goto,', idl[goto_lineNum].lower(), skipums); # Regex it
                        if( regexr_if is not None ):
                            realTest = idl[goto_lineNum][regexr_if.start():regexr_if.end()]; # Temp hold the line here
                            realTest = realTest[realTest.find('if')+2:realTest.find('then')].strip(' '); # Get the real test to use in the while statement out of the if statement
                            FLG_spacer = 1; # Move it up for next time
                            idl[goto_lineNum] = 'endwhile'; # Yee boi
                            if( realTest.find(' ') == -1 ):
                                bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'while( '+realTest+' ):'); # Create the cool af while statement
                                FLG_defined = False # Assume not defined
                                for j in range(i-1, -1, -1):
                                    regexr_defined = regex_avoid(r'^\s*'+realTest+r' *=', bevItUp.lower(), skipums); # Regex it
                                    if( regexr_defined is not None ):
                                        FLG_defined = True; # Yay, no effort
                                        break; # Escape
                                    # END IF
                                # END FOR j
                                if( FLG_defined == False ):
                                    codez4later.append(realTest+' = True'); # Ensure it is defined and makes the while loop start
                                # END IF
                            else:
                                # Not ewhat the code things the while statement should be
                                # print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; the line in question:');
                                # print(bevItUp);
                                # print('The single "goto" line call:')
                                # print(idl[goto_lineNum])
                                # print('Depended on a logic statement not a variable. It was:');
                                # print(realTest);
                                # print('That means it\'s not supported. And it may not be ever supported. Refactor this yourself!');
                                print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; sorry fix it.');
                                bevItUp = bevItUp + ' -> while( '+realTest+' ):';
                            # END IF
                        else:
                            # print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; the line in question:');
                            # print(bevItUp);
                            # print('The single "goto" line call:')
                            # print(idl[goto_lineNum])
                            # print('Was not an if statement. That means it\'s not supported. And it may not be ever supported. Refactor this yourself!');
                            print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; sorry fix it.');
                        # END IF
                    else:
                        # print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; the line in question:');
                        # print(bevItUp);
                        # if( FLG_goto == 0 ):
                        #     print('No "goto, '+trigWord+'" calls were found, it means it likely is an if statement that looks behind itself. Unsupported (and may never be). Refactor this yourself!');
                        # else:
                        #     print(str(FLG_goto)+' "goto, '+trigWord+'" calls were found, it means that it\'s calling the goto in a bunch of places. Unsupported (and may never be). Refactor this yourself!');
                        # # END IF
                        print('WARNING in idl2py: A goto definition statement was detected at line '+str(i)+'; sorry fix it.');
                    # END IF
                # END IF
                
                # & statement split
                regexrL = regex_avoid_logic(r'&', bevItUp, skipums); # Regex it
                if( regexrL == True ):
                    # Got a line split, could be many
                    while(  regex_avoid_logic(r'&', bevItUp, skipums, FLG_rev=True) ):
                        regexr = regex_avoid(r'&', bevItUp, skipums, FLG_rev=True); # Get where that last & at
                        idl.insert(i+1,bevItUp[regexr.end():]); # Split at "then", put it into IDL for later (basically making it a real if statement)
                        fend += 1; # More fend to cover
                        bevItUp = bevItUp[:regexr.start()]; # Remove the split bit, add a :
                    # END WHILE
                # END IF
                
                # Function call, yolo mode
                # alexa laser eyes idl
                FLG_forceFun = r','; # Flag for forced function
                regexr_fun = regex_avoid(r'^\s*\w+ *,', bevItUp, skipums); # Regex it
                # regexr_fun_reject = regex_avoid(r'^\s*\w+ *,.*=', bevItUp, skipums); # Regex it (this is hard b/c "message,/CON, NoPrint= Silent,'message'" can occur and stuff while we want "skymod, skysig, skyskw = mmm( skybuf, readnoise=readnoise, minsky=minsky )" to be ignored
                if( regexr_fun is None ):
                    for jj in range(0, len(forceImport)):
                        regexr_fun = regex_avoid(forceImport[jj]+r' *\(', bevItUp, skipums); # Regex it
                        if( regexr_fun is not None ):
                            FLG_forceFun = r'\('; # Special time
                            break; # Yeet out
                        # END IF
                    # END FOR jj
                # END IF
                if( regexr_fun is not None ):
                    # Remove the front stuff
                    regexr_fun = regex_avoid(r'\w+ *'+FLG_forceFun, bevItUp[:regexr_fun.end()], skipums); # Regex it
                    funName = bevItUp[regexr_fun.start():regexr_fun.end()-1].strip(' ').lower(); # Get the function name
                    regexr_fun_avoidRecurse = False; # Avoid infinite recursiveness, basically a function can call another function which calls it all within the same file. This prevents the input/output analysis as it is right now. So just avoid it.
                    for gg in range(funt, fend):
                        regexr_fun_avoidRecurse |= regex_avoid(r'^\s*pro *'+funName+r' *,', idl[gg].lower(), None, FLG_logic = True); # Regex it
                    # END FOR gg
                    if( funName == 'fxaddpar' ):
                        regexr_fun_avoidRecurse = True; # This one calls another function within that calls back to it, so that's hard to ponder so I'm just moving on for now
                    # END IF
                    if( regexr_fun_avoidRecurse == True ):
                        print('WARNING: "'+funName+'.pro" calls itself recursively and will NOT be analysed!');
                    # END IF
                                        
                    if( (regexr_fun_avoidRecurse == False ) and ((funName in convertedCache) or (funName in funName_included)) ): # Rev up the cache to check it
                        # Get the report var outa the cache, no need to read it again
                        if( funName in convertedCache ):
                            defy_report_fun = convertedCache[funName]['report'];
                            
                            # --- Insert the import as needed ---
                            if( funName not in importedMemory ):
                                if( libDir == None ):
                                    codez.insert(0, 'from '+funName+' import '+funName ); # Get the import at the top
                                else:
                                    codez.insert(0, 'from '+os.path.basename(libDir)+'.'+funName+' import '+funName ); # Get the import at the top
                                # END IF
                                importOffset += 1; # Increment the offset
                                importedMemory.append(funName); # Add it on
                            # END IF
                        else:
                            # Then it's in funName_included
                            defy_report_fun = convertedCache_local[funName]['report'];
                        # END IF
                        
                        # --- Ascertain which are inputs or outputs or whatever ---
                        rejiggered = bevItUp[regexr_fun.end():]; # Split it up (will need more when there's a line continuation
                        if( rejiggered.find(';') > -1 ):
                            rejiggered = rejiggered[:rejiggered.find(';')]; # Yeet this off
                        # END IF
                        rejiggered = splitterz(rejiggered, ',', splitums+[['(',')']]); # Break it apart, but good
                        # rejiggered = rejiggered.split(','); # Break it apart
                        rejiggered = [bitty.strip(' ') for bitty in rejiggered]; # Make sure no spaces
                        rejiggered_defs = [None for _ in rejiggered]; # Prep this
                        for gg in range(0, len(rejiggered)):
                            if( rejiggered[gg].find('=') > -1 ):
                                rejiggered_defs[gg] = 'default;'+rejiggered[gg][:rejiggered[gg].find('=')]; # Yee boi
                            else:
                                rejiggered_defs[gg] = defy_report_fun[gg]; # Use it directly
                            # END IF
                        # END FOR gg
                        
                        # --- Convert the line ---
                        rejiggered_ins = [];
                        rejiggered_outs = [];
                        rejiggered_defaults = [];
                        for gg in range(0, len(rejiggered)):
                            if( rejiggered_defs[gg] == 'input' ):
                                rejiggered_ins.append(rejiggered[gg]); # Tack it on
                            elif( rejiggered_defs[gg] == 'output' ):
                                rejiggered_outs.append(rejiggered[gg]); # Tack it on
                            elif( 'default;' in rejiggered_defs[gg] ):
                                if( '/' in rejiggered[gg] ):
                                    # Catch this switch thing, use the var name after / and set to True, it's a switch
                                    rejiggered_defaults.append(rejiggered[gg][rejiggered[gg].find('/')+1:]+' = True'); # Tack it on
                                else:
                                    rejiggered_defaults.append(rejiggered[gg]); # Tack it on
                                # END IF
                            # END IF
                        # END FOR gg
                        if( FLG_forceFun == r',' ):
                            if( bevItUp.find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                if( len(rejiggered_defaults) > 0 ):
                                    bevItUp += ', '+', '.join(rejiggered_defaults)+' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                else:
                                    bevItUp += ' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                # END IF
                            else:
                                bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                if( len(rejiggered_defaults) > 0 ):
                                    bevItUp += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                else:
                                    bevItUp += ' )'; # Badabing, badaboom
                                # END IF
                            # END IF
                            if( len(rejiggered_outs) == 0 ):
                                regexr_emptyEq = regex_avoid(r'^\s*= *', bevItUp, skipums);
                                if( regexr_emptyEq is not None ):
                                    bevItUp = strreplace(bevItUp, regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                # END IF
                            # END IF
                        else:
                            # This was called as a function so check for an ='s and if it's there don't bother
                            if( bevItUp.find('=') > -1 ):
                                paren_match = parenthesis_hunter(bevItUp[regexr_fun.start():])+regexr_fun.start();
                                bit_inside = bevItUp[regexr_fun.end():paren_match].split(',');
                                for jj in range(0, len(bit_inside)):
                                    bit_inside[jj] = bit_inside[jj].strip(' ');
                                    if( bit_inside[jj][0] == '/' ):
                                        bit_inside[jj] = bit_inside[jj][1:]+' = True'; # Make it better
                                    # END IF
                                # END FOR jj
                                bit_inside = ', '.join(bit_inside); # REBUILD
                                bevItUp = strreplace(bevItUp, regexr_fun.end(), paren_match, bit_inside)
                            else:
                                if( bevItUp.find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                    bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                    if( len(rejiggered_defaults) > 0 ):
                                        bevItUp += ', '+', '.join(rejiggered_defaults)+' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                    else:
                                        bevItUp += ' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                    # END IF
                                else:
                                    bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                    if( len(rejiggered_defaults) > 0 ):
                                        bevItUp += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                    else:
                                        bevItUp += ' )'; # Badabing, badaboom
                                    # END IF
                                # END IF
                                if( len(rejiggered_outs) == 0 ):
                                    regexr_emptyEq = regex_avoid(r'^\s*= *', bevItUp, skipums);
                                    if( regexr_emptyEq is not None ):
                                        bevItUp = strreplace(bevItUp, regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                    # END IF
                                # END IF
                            # END IF
                        # END IF
                    elif( (regexr_fun_avoidRecurse == False ) and (funName not in builtIns) ):
                        # --- Determine function file and where it at ---
                        # Look in the library paths
                        finds = glob(os.path.join(os.getcwd(),'**',funName+'.pro'), recursive=True); # Glob it up
                        if( len(finds) > 0 ):
                            # --- Read in IDL file ---
                            with open(finds[0], 'r') as file: # use 1st hit
                                idl_fun = [line.rstrip() for line in file];
                            # END WITH

                            # --- Rip into it ---
                            # Even if it is already converted, need defy_report to know if things are 
                            print('\n--- ON '+finds[0]+' ---');
                            codez_fun, defy_report_fun = trans( idl_fun, libDir = libDir ); # Translate from IDL to Python (in function form so can recursive if it finds OTHER IDL files)

                            # --- Save converted Python ---
                            # finds = glob(os.path.join(os.getcwd(),'**',funName+'.py'), recursive=True); # Glob it up (this was to check if already had it written, but it might need updating or something so might as well just do it)
                            if( libDir == None ):
                                with open(os.path.join(os.getcwd(),funName+'.py'), 'w') as file:
                                    file.write('\n'.join(linez for linez in codez_fun));
                                # END WITH
                            else:
                                with open(os.path.join(libDir,funName+'.py'), 'w') as file:
                                    file.write('\n'.join(linez for linez in codez_fun));
                                # END WITH
                            # END IF
                            
                            # --- Insert the import as needed ---
                            if( funName not in importedMemory ):
                                if( libDir == None ):
                                    codez.insert(0, 'from '+funName+' import '+funName ); # Get the import at the top
                                else:
                                    codez.insert(0, 'from '+os.path.basename(libDir)+'.'+funName+' import '+funName ); # Get the import at the top
                                # END IF
                                importOffset += 1; # Increment the offset
                                importedMemory.append(funName); # Add it on
                            # END IF
                            
                            # --- Ascertain which are inputs or outputs or whatever ---
                            rejiggered = bevItUp[regexr_fun.end():]; # Split it up (will need more when there's a line continuation
                            if( rejiggered.find(';') > -1 ):
                                rejiggered = rejiggered[:rejiggered.find(';')]; # Yeet this off
                            # END IF
                            rejiggered = splitterz(rejiggered, ',', splitums+[['(',')']]); # Break it apart, but good
                            # rejiggered = rejiggered.split(','); # Break it apart
                            rejiggered = [bitty.strip(' ') for bitty in rejiggered]; # Make sure no spaces
                            rejiggered_defs = [None for _ in rejiggered]; # Prep this
                            for gg in range(0, len(rejiggered)):
                                if( rejiggered[gg].find('=') > -1 ):
                                    rejiggered_defs[gg] = 'default;'+rejiggered[gg][:rejiggered[gg].find('=')]; # Yee boi
                                else:
                                    rejiggered_defs[gg] = defy_report_fun[gg]; # Use it directly
                                # END IF
                            # END FOR gg
                            
                            # --- Convert the line ---
                            rejiggered_ins = [];
                            rejiggered_outs = [];
                            rejiggered_defaults = [];
                            for gg in range(0, len(rejiggered)):
                                if( rejiggered_defs[gg] == 'input' ):
                                    rejiggered_ins.append(rejiggered[gg]); # Tack it on
                                elif( rejiggered_defs[gg] == 'output' ):
                                    rejiggered_outs.append(rejiggered[gg]); # Tack it on
                                elif( 'default;' in rejiggered_defs[gg] ):
                                    if( '/' in rejiggered[gg] ):
                                        # Catch this switch thing, use the var name after / and set to True, it's a switch
                                        rejiggered_defaults.append(rejiggered[gg][rejiggered[gg].find('/')+1:]+' = True'); # Tack it on
                                    else:
                                        rejiggered_defaults.append(rejiggered[gg]); # Tack it on
                                    # END IF
                                else:
                                    # Tack extra stuff onto the outs
                                    rejiggered_outs.append(rejiggered[gg]); # Tack it on
                                # END IF
                            # END FOR gg
                            if( FLG_forceFun == r',' ):
                                if( bevItUp.find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                    bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                    if( len(rejiggered_defaults) > 0 ):
                                        bevItUp += ', '+', '.join(rejiggered_defaults)+' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                    else:
                                        bevItUp += ' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                    # END IF
                                else:
                                    bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                    if( len(rejiggered_defaults) > 0 ):
                                        bevItUp += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                    else:
                                        bevItUp += ' )'; # Badabing, badaboom
                                    # END IF
                                # END IF
                                if( len(rejiggered_outs) == 0 ):
                                    regexr_emptyEq = regex_avoid(r'^\s*= *', bevItUp, skipums);
                                    if( regexr_emptyEq is not None ):
                                        bevItUp = strreplace(bevItUp, regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                    # END IF
                                # END IF
                            else:
                                # This was called as a function so check for an ='s and if it's there don't bother
                                if( bevItUp.find('=') > -1 ):
                                    paren_match = parenthesis_hunter(bevItUp[regexr_fun.start():])+regexr_fun.start();
                                    bit_inside = bevItUp[regexr_fun.end():paren_match].split(',');
                                    for jj in range(0, len(bit_inside)):
                                        bit_inside[jj] = bit_inside[jj].strip(' ');
                                        if( bit_inside[jj][0] == '/' ):
                                            bit_inside[jj] = bit_inside[jj][1:]+' = True'; # Make it better
                                        # END IF
                                    # END FOR jj
                                    bit_inside = ', '.join(bit_inside); # REBUILD
                                    bevItUp = strreplace(bevItUp, regexr_fun.end(), paren_match, bit_inside)
                                else:
                                    if( bevItUp.find(';') > -1 ): # This will likely have to get more intense if $ occurs
                                        bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                        if( len(rejiggered_defaults) > 0 ):
                                            bevItUp += ', '+', '.join(rejiggered_defaults)+' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                        else:
                                            bevItUp += ' ) '+bevItUp[bevItUp.find(';'):]; # Badabing, badaboom
                                        # END IF
                                    else:
                                        bevItUp = bevItUp[:regexr_fun.start()]+', '.join(rejiggered_outs)+' = '+funName+'( '+', '.join(rejiggered_ins); # Deal with defaults next
                                        if( len(rejiggered_defaults) > 0 ):
                                            bevItUp += ', '+', '.join(rejiggered_defaults)+' )'; # Badabing, badaboom
                                        else:
                                            bevItUp += ' )'; # Badabing, badaboom
                                        # END IF
                                    # END IF
                                    if( len(rejiggered_outs) == 0 ):
                                        regexr_emptyEq = regex_avoid(r'^\s*= *', bevItUp, skipums);
                                        if( regexr_emptyEq is not None ):
                                            bevItUp = strreplace(bevItUp, regexr_emptyEq.start(), regexr_emptyEq.end(), ''); # pew pew
                                        # END IF
                                    # END IF
                                # END IF
                            # END IF
                            
                            print('--- DONE WITH '+finds[0]+' ---');
                        else:
                            print('WARNING: "'+funName+'.pro" was not found in the libs!');
                            print('Line in question: \n'+bevItUp);
                            print('Ignoring. Find it and this incantation will transform it too!\n');
                        # END IF
                    elif( (regexr_fun_avoidRecurse == True ) or (False) ):
                        # Since can't analyse, return all things that went in - future may need to parse the IDL function comments
                        regexr_comment = regex_avoid(r' *;', idl[jk], None); # Regex it
                        if( regexr_comment is None ):
                            endy = ''; # Nothing to end with
                            endy_indx = len(bevItUp); # End is the end
                        else:
                            endy = bevItUp[regexr_comment.start():]; # The endy call
                            endy_indx = regexr_comment.start(); # End is the comment start
                        # END IF
                        
                        reals = splitterz(bevItUp[regexr_fun.end():endy_indx], ',', splitums+[['(',')']]); # Get the inputs
                        eq_ops = [];
                        slash_ops = [];
                        for jj in range(len(reals)-1, -1, -1):
                            if( '=' in reals[jj] ):
                                eq_ops.append(reals[jj].strip(' ')); # Record
                                reals.pop(jj); # Yeet
                            elif( '/' == reals[jj].strip(' ')[0] ):
                                slash_ops.append(reals[jj].strip(' ')); # Record
                                reals.pop(jj); # Yeet
                            else:
                                reals[jj] = reals[jj].strip(' '); # Remove spaces just in case
                            # END IF
                        # END FOR jj
                        if( len(slash_ops) > 0 ): # Didn't work this one out, should be fast at least sorry future me
                            breakpoint()
                            pass
                        # END IF
                        reals_out = reals.copy(); # out doesn't need numbers
                        for jj in range(len(reals_out)-1, -1, -1):
                            if( reals_out[jj][0].isnumeric() ): # Assume variables can't start with a number
                               reals_out.pop(jj); # Yeet
                           # END IF
                        # END FOR jj
                        
                        # Rehydrate
                        bevItUp = ', '.join(reals_out)+' = '+funName+'( '+', '.join(reals + eq_ops + slash_ops)+' )'+endy; # Rebuild but better
                    # END IF
                # END IF
                
                # message
                regexr = regex_avoid(r'message *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    # Nuke /STUFF - prob want to read them if make function that mimics message more
                    regexr_backslash = regex_avoid(r'(/\w+ *,)|(,/\w+ *$)', bevItUp.lower(), skipums); # Regex it
                    while( regexr_backslash is not None ):
                        bevItUp = strreplace( bevItUp, regexr_backslash.start(), regexr_backslash.end(), '' ); # Replace the bit!
                        regexr_backslash = regex_avoid(r'(/\w+ *,)|(,/\w+ *$)', bevItUp.lower(), skipums); # Regex it
                    # END WHILE
                    
                    regexr_noprint = regex_avoid(r'(noprint *=.*,)|(,noprint *=.*$)', bevItUp[regexr.end():].lower(), skipums); # Regex it
                    if( regexr_noprint is not None ):
                        # This requires an if statement - maybe in the future if needed message can have a helper function that does this, for now yolo
                        ifwhat = bevItUp[regexr.end()+bevItUp[regexr.end():].find('=')+1:regexr.end()+regexr_noprint.end()-1].strip(' '); # Get the variable to check in the if statment
                        bevItUp = strreplace( bevItUp, regexr.end()+regexr_noprint.start(), regexr.end()+regexr_noprint.end(), '' ); # Replace the bit!
                        printwhat = bevItUp[regexr.end():]; # What is gonna be printed
                        regexr_printwhat = regex_avoid(r'\s*\$ *(\n|\\n) *', printwhat.lower(), skipums); # Regex it
                        if( regexr_printwhat is not None ):
                            printwhat = strreplace( printwhat, regexr_printwhat.start(), regexr_printwhat.end(), '' ); # Replace the bit!
                        # END IF
                        idl.insert(i+1, 'print, '+printwhat);
                        idl.insert(i+2, 'endif');
                        fend += 2; # More fend to cover
                        bevItUp = 'if( '+ifwhat+' == True ):'; # The if statement needed
                        FLG_IF_open += 1; # Great
                        FLG_lastOpen.append('if');
                        FLG_spacer = 1; # Move it up for next time
                    else:
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'print(' ); # Replace the bit!
                        bevItUp += ')' ; # Close the parentheses
                    # END IF
                # END IF
                
                # print - may get more intense
                regexr = regex_avoid(r'print *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'print(' ); # Replace the bit!
                    regexr_comment = regex_avoid(r' *;', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        endy = ''; # Nothing to end with
                    else:
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                        bevItUp = strreplace(bevItUp, regexr_comment.start(), len(bevItUp), ''); # Yeet the comment
                    # END IF
                    bevItUp += ')'+endy ; # Close the parentheses
                # END IF
                
                # printf - holder for now
                regexr = regex_avoid(r'printf *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'printf(' ); # Replace the bit!
                    regexr_comment = regex_avoid(r' *;', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        endy = ''; # Nothing to end with
                    else:
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                        bevItUp = strreplace(bevItUp, regexr_comment.start(), len(bevItUp), ''); # Yeet the comment
                    # END IF
                    bevItUp += ')'+endy ; # Close the parentheses
                # END IF
                
                # remchar - this is a custom one, but it's ez pz in python
                regexr = regex_avoid(r'remchar *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    var2do_endComma = bevItUp[regexr.end():].find(',')+regexr.end(); # Where it at
                    var2do = bevItUp[regexr.end():var2do_endComma]; # The var to work on
                    regexr = regex_avoid(r'(,.+$|,.+;|,.+\$)', bevItUp[var2do_endComma:], skipums); # Regex it
                    try:
                        var2ditch = bevItUp[regexr.start()+var2do_endComma+1:regexr.end()+var2do_endComma+1].strip(' '); # Get the thing to ditch
                    except:
                        breakpoint()
                        regexr = regex_avoid(r'(,.+$|,.+;|,.+\$)', bevItUp[var2do_endComma:], skipums); # Regex it
                    bevItUp = var2do+' = '+var2do+'.replace('+var2ditch+', \'\')'; # Replace the bit!
                # END IF
                
                # strtrim
                regexr = regex_avoid(r'strtrim *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    endparenth = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # Yee
                    regexr_flag = regex_avoid(r'\( *[0-9] *,', mirrorU(bevItUp[regexr.start():endparenth]), skipums); # Regex it
                    if( regexr_flag is not None ):
                        regexr_flag_start = endparenth-regexr_flag.end();
                        regexr_flag_end = endparenth-regexr_flag.start(); # Undo the mirror universe
                        regexr_flagNum = regex_avoid(r'[0-9]', bevItUp[regexr_flag_start:regexr_flag_end], skipums); # Regex it
                        regexr_flagNum = bevItUp[regexr_flag_start+regexr_flagNum.start():regexr_flag_start+regexr_flagNum.end()]; # Just get that number
                        if( regexr_flagNum == '0' ):
                            bevItUp = strinsert(bevItUp, endparenth, ".rstrip(' ')"); # Keep the strtrim call correct in case it's actually needed (seems a crutch for IDL mostly)
                        elif( regexr_flagNum == '1' ):
                            bevItUp = strinsert(bevItUp, endparenth, ".lstrip(' ')"); # Keep the strtrim call correct in case it's actually needed (seems a crutch for IDL mostly)
                        elif( regexr_flagNum == '2' ):
                            bevItUp = strinsert(bevItUp, endparenth, ".strip(' ')"); # Keep the strtrim call correct in case it's actually needed (seems a crutch for IDL mostly)
                        else:
                            print('unknown??')
                            breakpoint()
                        # END IF
                        bevItUp = strreplace(bevItUp, regexr_flag_start, regexr_flag_end, ')'); # Remove the comma and number flag
                    else:
                        bevItUp = strinsert(bevItUp, endparenth, ".rstrip(' ')"); # Keep the strtrim call correct in case it's actually needed (seems a crutch for IDL mostly)
                    # END IF
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), 'str('); # Replace the strrim call
                    regexr = regex_avoid(r'strtrim *\(', bevItUp.lower(), skipums); # Regex it, make sure to get em all
                # END WHILE
                
                # strupcase
                regexr = regex_avoid(r'strupcase *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    endparenth = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # Yee
                    bevItUp = strinsert(bevItUp, endparenth, '.upper()'); # Keep the strtrim call correct in case it's actually needed (seems a crutch for IDL mostly)
                    bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), 'str('); # Replace the strrim call
                    regexr = regex_avoid(r'strupcase *\(', bevItUp.lower(), skipums); # Regex it, make sure to get em all
                # END WHILE
                
                # N_elements
                regexr = regex_avoid(r'(n_elements *\(\s*\w+\s*\))', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    repl = bevItUp[regexr.start():regexr.end()]; # Get the thing to replace
                    repl = 'len( '+repl[repl.find('(')+1:repl.rfind(')')]+' )'; # Make a new, good strang
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), repl ); # Replace the bit!
                    
                    regexr = regex_avoid(r'(n_elements *\(\s*\w+\s*\))', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # PLOT SERIES: window
                regexr = regex_avoid(r'^\s*window *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('ERROR in window: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    if( len(reals) == 2 ):
                        for jj in range(0, len(reals)):
                            if( 'xsize' in reals[jj] ):
                                xsize = reals[jj][reals[jj].find('=')+1:];
                            elif( 'ysize' in reals[jj] ):
                                ysize = reals[jj][reals[jj].find('=')+1:];
                            # END IF
                        # END FOR jj
                        codez4later.append('fig = plt.figure(figsize=('+xsize+"*1/plt.rcParams['figure.dpi'], "+ysize+"*1/plt.rcParams['figure.dpi']))"); # Direct write in
                        bevItUp = 'ax = fig.add_subplot(111)'; # Replace the bit! This is pretty rigid  so deal with it if it doesn't work later
                    else:
                        print('ERROR in window: unsupported length for inputs to plt.figure: '+str(reals));
                        breakpoint()
                    # END IF
                    importz['plt'] = True; # Get it
                    FLG_plt_windowCalled = True; # Window was called, so there's a window
                # END IF
                
                # PLOT SERIES: plot/oplot
                regexr = regex_avoid(r'^\s*o?plot *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    # oplot just means add it to a new axis, so whatever
                    FLG_is_oplot = 'oplot' in bevItUp[regexr.start():regexr.end()].lower(); # Is it oplot instead of plot?
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('ERROR in window: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    plt_symbol = None; # None, it's a plot
                    plt_lineStyle = None; # Regular
                    plt_color = None; # Regular
                    lines2add = []; # Build as needed
                    eq_ops = [];
                    slash_ops = [];
                    for jj in range(len(reals)-1, -1, -1):
                        if( '=' in reals[jj] ):
                            eq_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        elif( '/' == reals[jj].strip(' ')[0] ):
                            slash_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        else:
                            reals[jj] = reals[jj].strip(' '); # Remove spaces just in case
                        # END IF
                    # END FOR jj
                    
                    # Equal options here
                    for jj in range(0, len(eq_ops)):
                        if( 'xrange' == eq_ops[jj][0:6].lower() ):
                            lines2add.append('ax.set_xlim( '+eq_ops[jj][eq_ops[jj].find('=')+1:]+' )' ); #set x axis limits
                        elif( 'yrange' == eq_ops[jj][0:6].lower() ):
                            lines2add.append('ax.set_ylim( '+eq_ops[jj][eq_ops[jj].find('=')+1:]+' )' ); #set x axis limits
                        elif( 'psym' == eq_ops[jj][0:4].lower() ):
                            if( '1' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'P'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '2' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'*'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '3' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'.'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '4' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'D'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '5' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'^'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '6' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'s'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            elif( '7' == eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' ') ):
                                plt_symbol = "'X'"; # It's time
                                plt_lineStyle = "'None'"; # No line to go with, it's a scatter with extra steps!
                            else:
                                print('ERROR: Unsupported psym plot option. Fix it.');
                                breakpoint(); # Trying this out
                            # END IF
                        elif( 'color' == eq_ops[jj][0:5].lower() ):
                            plt_color = eq_ops[jj][eq_ops[jj].find('=')+1:].strip(' '); # Get the color
                            if( plt_color[-1] == 'x' ):
                                plt_color = plt_color[:-1]; # Ditch the x
                                plt_color = strinsert(plt_color, 1, '#'); # Slam a # at the front
                            else:
                                print('ERROR: Unsupported plot option. Fix it.');
                                breakpoint(); # Trying this out
                            # END IF
                        elif( 'charsize' == eq_ops[jj][0:8].lower() ):
                            pass # Don't care
                        elif( 'xmargin' == eq_ops[jj][0:7].lower() ):
                            pass # Don't care
                        elif( 'ymargin' == eq_ops[jj][0:7].lower() ):
                            pass
                        elif( 'xtitle' == eq_ops[jj][0:6].lower() ):
                            lines2add.append( 'ax.set_xlabel( '+eq_ops[jj][eq_ops[jj].find('=')+1:]+' )' ); #set x axis title
                        elif( 'ytitle' == eq_ops[jj][0:6].lower() ):
                            lines2add.append( 'ax.set_ylabel( '+eq_ops[jj][eq_ops[jj].find('=')+1:]+' )' ); #set x axis title
                        elif( 'xstyle' == eq_ops[jj][0:6].lower() ):
                            pass # For now, these seem superfluous
                        elif( 'ystyle' == eq_ops[jj][0:6].lower() ):
                            pass
                        else:
                            print('ERROR: Unsupported plot option. Fix it.\n'+eq_ops[jj]);
                            breakpoint(); # Trying this out
                        # END IF
                    # END FOR jj
                    
                    # Slash options here
                    for jj in range(0, len(slash_ops)):
                        if( '/xstyle' == slash_ops[jj][0:7].lower() ):
                            pass # For now, these seem superfluous
                        elif( '/ystyle' == slash_ops[jj][0:7].lower() ):
                            pass
                        elif( '/xlog' == slash_ops[jj][0:5].lower() ):
                            lines2add.append("ax.set_xscale('log')");
                        elif( '/ylog' == slash_ops[jj][0:5].lower() ):
                            lines2add.append("ax.set_yscale('log')");
                        else:
                            print('ERROR: Unsupported plot option. Fix it.');
                            breakpoint(); # Trying this out
                        # END IF
                    # END FOR jj
                    
                    # Actual plot call here
                    actual_plot = 'ax.plot( '; # Get it started
                    for jj in range(0, len(reals)):
                        actual_plot += reals[jj]+', '; # Build it up
                    # END FOR jj
                    if( plt_symbol != None ):
                        actual_plot += 'marker='+plt_symbol+', '; # Build it up
                        if( plt_color != None ):
                            actual_plot += 'markeredgecolor='+plt_color+', '; # Build it up
                            actual_plot += 'markerfacecolor='+plt_color+', '; # Build it up
                        # END IF
                    # END IF
                    if( plt_lineStyle != None ):
                        actual_plot += 'linestyle='+plt_lineStyle+', '; # Build it up
                        if( (plt_color != None) and (plt_lineStyle != 'None') ):
                            actual_plot += 'color='+plt_color+', '; # Build it up
                        # END IF
                    # END IF
                    actual_plot = actual_plot[:-2]+' )'; # Cap it off
                    if( endy != '' ):
                        actual_plot += ' #'+endy[1:]; # Tag it on
                    # END IF
                    # lines2add.append(actual_plot); # Just slam it on
                    
                    if( FLG_plt_windowCalled == False ):
                        FLG_plt_windowCalled = True; # Window was called, so there's a window
                        codez4later.append('fig = plt.figure()'); # Direct write in
                        codez4later.append('ax = fig.add_subplot(111)'); # Direct write in
                        importz['plt'] = True; # Get it
                    # END IF
                    
                    # Build it!~
                    if( (FLG_is_oplot == False) and (FLG_plt_windowCalled == True) ):
                        codez4later.append('ax.clear()'); # Clear out the axis, supports reuse
                    # END IF
                    # if( len(lines2add) > 0 ):
                    codez4later.append(actual_plot); # Yeeboi
                    for jj in range(0, len(lines2add) ):
                        codez4later.append(lines2add[jj]); # Yeeboi
                    # END FOR jj
                    #     bevItUp = lines2add[-1]; # Tack it on
                    # else:
                    #     bevItUp = actual_plot; #Slap it on
                    # # END IF
                    bevItUp = 'plt.show(block=False)'; # End every plot call with an explicit plot show call
                # END IF
                                
                # PLOT SERIES: xyouts
                regexr = regex_avoid(r'^\s*xyouts *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('ERROR in window: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    plt_keyz = {}; # Dict to hold keys to tell me if something happened later, galaxy brain
                    lines2add = []; # Build as needed
                    eq_ops = [];
                    slash_ops = [];
                    for jj in range(len(reals)-1, -1, -1):
                        if( '=' in reals[jj] ):
                            eq_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        elif( '/' == reals[jj].strip(' ')[0] ):
                            slash_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        else:
                            reals[jj] = reals[jj].strip(' '); # Remove spaces just in case
                        # END IF
                    # END FOR jj
                    
                    # Equal options here
                    for jj in range(0, len(eq_ops)):
                        if( 'charsize' == eq_ops[jj][0:8].lower() ):
                            pass # Don't care
                        else:
                            print('ERROR: Unsupported xyout option. Fix it.\n'+eq_ops[jj]);
                            breakpoint(); # Trying this out
                        # END IF
                    # END FOR jj
                    
                    # Slash options here
                    for jj in range(0, len(slash_ops)):
                        if( '/normal' == slash_ops[jj][0:7].lower() ):
                            plt_keyz['normal'] = True; # Fire that key up
                        else:
                            print('ERROR: Unsupported plot option. Fix it.');
                            breakpoint(); # Trying this out
                        # END IF
                    # END FOR jj
                    
                    # Actual plot call here
                    actual_plot = 'ax.text( '; # Get it started
                    for jj in range(0, len(reals)):
                        actual_plot += reals[jj]+', '; # Build it up
                    # END FOR jj
                    #horizontalalignment='center',verticalalignment='center' <- may be needed for good match
                    if( 'normal' in plt_keyz ):
                        actual_plot += 'transform=ax.transAxes, '; # Build it up
                    # END IF
                    actual_plot = actual_plot[:-2]+' )'; # Cap it off
                    if( endy != '' ):
                        actual_plot += ' #'+endy[1:]; # Tag it on
                    # END IF
                    # lines2add.append(actual_plot); # Just slam it on
                    
                    if( FLG_plt_windowCalled == False ):
                        FLG_plt_windowCalled = True; # Window was called, so there's a window
                        codez4later.append('fig = plt.figure()'); # Direct write in
                        codez4later.append('ax = fig.add_subplot(111)'); # Direct write in
                        importz['plt'] = True; # Get it
                    # END IF
                    
                    # Build it!~
                    codez4later.append(actual_plot); # Yeeboi
                    for jj in range(0, len(lines2add) ):
                        codez4later.append(lines2add[jj]); # Yeeboi
                    # END FOR jj
                    bevItUp = 'plt.show(block=False)'; # End every plot call with an explicit plot show call
                # END IF
                
                # PLOT SERIES: !p.
                regexr = regex_avoid(r'!p.', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    if( regex_avoid_logic(r'^\s*!p.', bevItUp.lower(), skipums) ):
                        bevItUp = '@NUKETHISLINE'; # Nuke it, don't care rn
                    elif( regex_avoid_logic(r'= *!p.', bevItUp.lower(), skipums) ):
                        bevItUp = '@NUKETHISLINE'; # Nuke it, don't care rn
                    else:
                        print('Unseen use of !p., check it.')
                        breakpoint()
                    # END IF
                # END IF
                
                # PLOT SERIES: write_gif
                regexr = regex_avoid(r'^\s*write_gif *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('ERROR in write_gif: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    if( FLG_plt_gifWriter == False ):
                        
                        #--- This stuff is required to activate the gif making ---
                        codez4later.append('listFigs = {} # Dict that holds lists of figures, deliniated by output file names as keys for the dict');  
                                           
                        #--- This is required to save the gif at the end, matplotlib needs to do it in one go it seems ---
                        # I am sure there is a way to add a frame one at a time - it just seems that is a very niche thing and not talked about. So all at once!
                        if( FLG_FUN_idl_plt_gifWriter == False ):
                            # Get cookin
                            codez.insert( 0+importOffset, 'def idl_plt_gifWriter( currFig, listFigs ):');
                            codez.insert( 1+importOffset, '    # This uses the currFig as a place to put the saved figures');
                            codez.insert( 2+importOffset, "    FFMpegWriter = manimation.writers['ffmpeg']");
                            codez.insert( 3+importOffset, "    movie_writer = FFMpegWriter(fps=5, codec='gif', bitrate=25000) # Create a movie writer");
                            codez.insert( 4+importOffset, '    for keyz in listFigs:');
                            codez.insert( 5+importOffset, "        with movie_writer.saving(currFig, keyz, plt.rcParams['figure.dpi']): # plt.rcParams['figure.dpi'] is PPI");
                            codez.insert( 6+importOffset, '            for j in range(0,len(listFigs[keyz])):');
                            codez.insert( 7+importOffset, '                tempFig = pickle.loads(listFigs[keyz][j]); # Change the figure on the fly');
                            codez.insert( 8+importOffset, '                tempAxz = tempFig.axes; # Get the new axis handle');
                            codez.insert( 9+importOffset, "                currAxz = currFig.axes; # Get the current one too");
                            codez.insert(10+importOffset, '                for k in range(0,len(currAxz)):');
                            codez.insert(11+importOffset, '                    currAxz[k].remove(); # Disconnect from current figure with .remove()');
                            codez.insert(12+importOffset, '                # END FOR k');
                            codez.insert(13+importOffset, '                del currAxz # Remove');
                            codez.insert(14+importOffset, '                for k in range(0,len(tempAxz)):');
                            codez.insert(15+importOffset, '                    tempAxz[k].remove(); # Disconnect from temp figure with .remove()');
                            codez.insert(16+importOffset, '                # END FOR k');
                            codez.insert(17+importOffset, '                for k in range(0,len(tempAxz)):');
                            codez.insert(18+importOffset, '                    #attach to the current fig');
                            codez.insert(19+importOffset, "                    tempAxz[k].figure = currFig; # Attach to the currFig");
                            codez.insert(20+importOffset, "                    currFig.axes.append(tempAxz[k]); # \"register\" it");
                            codez.insert(21+importOffset, "                    currFig.add_axes(tempAxz[k]); # \"register\" it in another way");
                            codez.insert(22+importOffset, '                    ');
                            codez.insert(23+importOffset, '                # END FOR k');
                            codez.insert(24+importOffset, '                ');
                            codez.insert(25+importOffset, '                plt.close(tempFig); # Close it again');
                            codez.insert(26+importOffset, '                ');
                            codez.insert(27+importOffset, "                currFig.canvas.draw(); # Key for all instances");
                            codez.insert(28+importOffset, '                movie_writer.grab_frame(); # Get the frame and save it');
                            codez.insert(29+importOffset, '            # END FOR j');
                            codez.insert(30+importOffset, '        # END WITH');
                            codez.insert(31+importOffset, '    # END FOR keyz');
                            codez.insert(32+importOffset, '# END DEF');
                            codez.insert(33+importOffset, '');
                            
                            importz['pickle'] = True; # It's needed
                            FLG_FUN_idl_plt_gifWriter = True; # It's been added
                        # END IF
                        
                        if( reals[0] not in FLG_plt_gifWriter_names ):
                            codez4later.append('listFigs['+reals[0]+'] = [] # Begin a list of frames for the new output name key');
                            FLG_plt_gifWriter_names.append(reals[0]); # REcord the name of the file to save
                        # END IF
                        bevItUp = 'listFigs['+reals[0]+'].append(pickle.dumps(fig, protocol=pickle.HIGHEST_PROTOCOL)) # Save the figure for making into a gif later';
                        
                        importz['manimation'] = True; # Get it
                        FLG_plt_gifWriter = True; # Write the gif at the end of the function
                    else:
                        if( reals[0] not in FLG_plt_gifWriter_names ):
                            codez4later.append('listFigs['+reals[0]+'] = [] # Begin a list of frames for the new output name key');
                            FLG_plt_gifWriter_names.append(reals[0]); # REcord the name of the file to save
                        # END IF
                        bevItUp = 'listFigs['+reals[0]+'].append(pickle.dumps(fig, protocol=pickle.HIGHEST_PROTOCOL)) # Save the figure for making into a gif later';
                    # END IF
                    
                    if( FLG_plt_windowCalled == False ):
                        FLG_plt_windowCalled = True; # Window was called, so there's a window
                        codez4later.append('fig = plt.figure()'); # Direct write in
                        codez4later.append('ax = fig.add_subplot(111)'); # Direct write in
                        importz['plt'] = True; # Get it
                    # END IF
                    
                # END IF
                
                # FITS SERIES: readfits
                regexr = regex_avoid(r'readfits *\(', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end(); # Get the matching parenthesis (so we know where it ends)
                    repl = bevItUp[regexr.start():paren_match]; # Get the thing to replace
                    fitsVarName = bevItUp[:regexr.start()].replace('=','').strip(' ').strip('\t'); # Get the file name, gotta be the first
                    regexr_opts = regex_avoid(r'readfits *\( *', repl.lower(), skipums); # Regex it
                    # repl_opts = repl[regexr_opts.end():-1].split(','); # Isolate the input and options
                    repl_opts = splitterz(repl[regexr_opts.end():-1], ',', splitums+[['(',')']]); # Break it apart, but good
                    fitsFileName = repl_opts[0].strip(' '); # Get the file name, gotta be the first
                    codez4later.append('with fits.open('+fitsFileName+') as fitsFile:'); # Direct write in
                    # .T is added because it was clear to me from context that IDL somehow reads in the fits files transposed to what Astropy does, great right?
                    codez4later.append(' '*4+fitsVarName+' = fitsFile[0].data.T'+bevItUp[paren_match:].replace(';','#')); # Direct write in, carry over comments
                    for j in range(1, len(repl_opts)):
                        if( (repl_opts[j].strip(' ')[0] != '/') and (repl_opts[j].find('=') == -1) ):
                            # This puts the header stuff into a variable that sxpar works on
                            fitsHeaderVarName = repl_opts[j].strip(' '); # Get the header variable name
                            codez4later.append(fitsHeaderVarName+' = fitsFile[0].header'); # Direct write in
                        elif( repl_opts[j].strip(' ')[0] == '/' ):
                            if( repl_opts[j].strip(' ').lower() == '/silent' ):
                                pass # Don't care
                            else:
                                print('ERROR for readfits: NO SUPPORT FOR THIS / OPTION. ADD IT!');
                                breakpoint()
                            # END IF
                        elif( repl_opts[j].find('=') > -1 ):
                            print('ERROR for readfits: NO SUPPORT FOR = stuff. ADD IT!');
                            breakpoint()
                        # END IF
                    # END FOR j
                    
                    bevItUp = ' '*spacer+'; END WITH'; # Replace the bit!
                    
                    importz['astropy_fits'] = True; # It's needed                    
                # END IF
                
                # FITS SERIES: sxpar
                regexr = regex_avoid(r'sxpar *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    repl = bevItUp[regexr.end()-1:]; # Get the thing to replace
                    paren_match = parenthesis_hunter( repl ); # Get the matching parenthesis (so we know where it ends)
                    darest = repl[paren_match+1:]; # Rest is not sxpar stuff
                    repl = splitterz(repl[1:paren_match], ',', splitums); # Split it good
                    bevItUp = bevItUp[:regexr.start()]+repl[0]+'['+repl[1]+']'+darest; # Replace the bit!
                    
                    regexr = regex_avoid(r'sxpar *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # FITS SERIES: sxaddpar
                regexr = regex_avoid(r'^\s*sxaddpar *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('WARNING in sxaddpar: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    if( len(reals) == 4 ):
                        bevItUp = reals[0]+'['+reals[1]+'] = ('+reals[2]+', '+reals[3]+')'; # Replace the bit! This is pretty rigid  so deal with it if it doesn't work later
                    elif( len(reals) == 3 ):
                        bevItUp = reals[0]+'['+reals[1]+'] = '+reals[2]; # Replace the bit! It didn't work later wow
                    # END IF
                # END IF
                
                # readcol
                regexr = regex_avoid(r'^\s*readcol *,', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr_comment = regex_avoid(r';', bevItUp, None); # Regex it
                    if( regexr_comment is None ):
                        reals = bevItUp[regexr.end():]; # Get the stuff to work with
                        endy = ''; # Nothing to end with
                    else:
                        reals = bevItUp[regexr.end():regexr_comment.start()]; # Get the stuff to work with
                        endy = bevItUp[regexr_comment.start():]; # The endy call
                    # END IF
                    regexr_lineBreak = regex_avoid(r'\$\n *', reals, None); # Regex it
                    if( regexr_lineBreak is not None ):
                        regexr_lineBreakComment = regex_avoid(r';.*\$\n *', bevItUp, None); # Regex it
                        if( regexr_lineBreakComment is not None ):
                            print('WARNING in readcol: I didnt feel like writing this. If it happens, deal with it, sorry ufture me,.')
                            breakpoint()
                        else:
                            reals = strreplace( reals, regexr_lineBreak.start(), regexr_lineBreak.end(), '' ); # Replace the bit!
                        # END IF
                    # END IF
                    reals = splitterz(reals, ',', splitums); # Split it good
                    
                    ops = ''; # Options to add in, optionally
                    eq_ops = [];
                    slash_ops = [];
                    for jj in range(len(reals)-1, -1, -1):
                        if( '=' in reals[jj] ):
                            eq_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        elif( '/' == reals[jj].strip(' ')[0] ):
                            slash_ops.append(reals[jj].strip(' ')); # Record
                            reals.pop(jj); # Yeet
                        else:
                            reals[jj] = reals[jj].strip(' '); # Remove spaces just in case
                        # END IF
                    # END FOR jj
                    
                    # Equal options here
                    for jj in range(0, len(eq_ops)):
                        if( 'format' == eq_ops[jj][0:6].lower() ):
                            formaty = eq_ops[jj][eq_ops[jj].find('=')+1:]; # Whittle
                            formaty = splitterz(formaty[formaty.find("'")+1:formaty.rfind("'")], ',', splitums); # Down to just the real stuff
                            ops += ", dtype={"; # Begin the option
                            for jk in range(0, len(reals[1:])):
                                if( formaty[jk].strip().lower() == 'a' ):
                                    ops += "'"+reals[1:][jk]+"': str, "; # Build it
                                elif( formaty[jk].strip().lower() == 'b' ):
                                    ops += "'"+reals[1:][jk]+"': np.uint8, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'd' ):
                                    ops += "'"+reals[1:][jk]+"': np.float64, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'f' ):
                                    ops += "'"+reals[1:][jk]+"': np.float32, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'i' ):
                                    ops += "'"+reals[1:][jk]+"': np.int16, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'l' ):
                                    ops += "'"+reals[1:][jk]+"': np.int32, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'll' ):
                                    ops += "'"+reals[1:][jk]+"': np.int64, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'u' ):
                                    ops += "'"+reals[1:][jk]+"': np.uint16, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'ul' ):
                                    ops += "'"+reals[1:][jk]+"': np.uint32, "; # Build it
                                    importz['np'] = True; # Get it
                                elif( formaty[jk].strip().lower() == 'z' ): # Not sure about it ('longword hexadecimal')
                                    ops += "'"+reals[1:][jk]+"': str, "; # Build it
                                elif( formaty[jk].strip().lower() == 'x' ): # Not sure about this one ('skip a column')
                                    ops += "'"+reals[1:][jk]+"': str, "; # Build it
                                # END IF
                            # END FOR jk
                            ops = ops.rstrip(', ')+'}'; # Finish the op off
                        elif( 'skipline' == eq_ops[jj][0:8].lower() ):
                            skippy = eq_ops[jj][eq_ops[jj].find('=')+1:]; # Whittle
                            ops += ', skiprows='+skippy; # Finish the op off
                        else:
                            breakpoint(); # Trying this out
                            print('ERROR: Unsupported plot option. Fix it.\n'+eq_ops[jj]);
                        # END IF
                    # END FOR jj
                    
                    # Slash options here
                    for jj in range(0, len(slash_ops)):
                        if( '/fake' == slash_ops[jj][0:5].lower() ):
                            pass
                        else:
                            breakpoint(); # Trying this out
                            print('ERROR: Unsupported plot option. Fix it.\n'+slash_ops[jj]);
                        # END IF
                    # END FOR jj
                    
                    # Come back and add logic to figure out how many rows to skip if skiprows=# is needed
                    codez4later.append("pandasDataFrame = pd.read_csv("+reals[0]+", header=0, names="+str(reals[1:])+", sep=r'\\s+', engine='python'"+ops+")"+endy); # Replace the bit!
                    # Now build a way for the header names to become variable names
                    for keyz in reals[1:]:
                        codez4later.append('if( pd.api.types.is_numeric_dtype(pandasDataFrame[\''+keyz+'\'])):');
                        codez4later.append('    '+keyz+' = pandasDataFrame[\''+keyz+'\'].to_numpy() # Extract' );
                        codez4later.append('else:');
                        codez4later.append('    '+keyz+' = pandasDataFrame[\''+keyz+'\'].to_list() # Extract' ); # This may become to_numpy if list implementation turns out to be too weak
                        codez4later.append('# END IF');
                    # END FOR keyz
                    
                    bevItUp = codez4later[-1]; # Set it
                    codez4later.pop(-1); # Ditch it
                    importz['pd'] = True; # Get it
                # END IF
                    
                
                #  size
                regexr = regex_avoid(r'(?<!idl_where_)size *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    if( regex_avoid_logic(r', */structure', bevItUp.lower(), skipums) ):
                        regexr_equals = regex_avoid(r'\w+ *=', bevItUp, skipums); # Check for assignment (prob the case)
                        if( regexr_equals is not None ):
                            # Have to see how it is used and replace
                            origVar = bevItUp[regexr.end():bevItUp[regexr.end():].find(',')+regexr.end()]; # Get the orig var
                            var2check = bevItUp[regexr_equals.start():regexr_equals.end()-1].rstrip(' '); # Pull it out
                            bevItUp = var2check+' = idl_size_struct( '+origVar+' )' # Create a new bevItUp call for the new function
                            # --- Need a few things to mimic this --- 
                            # Need the mimicking function
                            if( FLG_FUN_idl_size_structure == False ):
                                # Get cookin'
                                codez.insert(0+importOffset, 'def idl_size_struct(var2heck):')
                                codez.insert(1+importOffset, '    class fakeStruct(object):')
                                codez.insert(2+importOffset, '        def __init__(self, type_nameV="", structure_nameV="", typeV=0, file_lunV=0, \\')
                                codez.insert(3+importOffset, '                     file_offsetnV=0, n_elementsV=0, n_dimensionsV=0, dimensionsV=[0, 0, 0, 0, 0, 0, 0, 0]):')
                                codez.insert(4+importOffset, '            self.type_nameV = type_nameV')
                                codez.insert(5+importOffset, '            self.structure_nameV = structure_nameV')
                                codez.insert(6+importOffset, '            self.typeV = typeV')
                                codez.insert(7+importOffset, '            self.file_lunV = file_lunV')
                                codez.insert(8+importOffset, '            self.file_offsetnV = file_offsetnV')
                                codez.insert(9+importOffset, '            self.n_elementsV = n_elementsV')
                                codez.insert(10+importOffset, '            self.n_dimensionsV = n_dimensionsV')
                                codez.insert(11+importOffset, '            self.dimensionsV = dimensionsV')
                                codez.insert(12+importOffset, '        # END DEF')
                                codez.insert(13+importOffset, '        def type_name(self):')
                                codez.insert(14+importOffset, '            return self.type_nameV')
                                codez.insert(15+importOffset, '        # END DEF')
                                codez.insert(16+importOffset, '        def structure_name(self):')
                                codez.insert(17+importOffset, '            return self.structure_nameV')
                                codez.insert(18+importOffset, '        # END DEF')
                                codez.insert(19+importOffset, '        def type(self):')
                                codez.insert(20+importOffset, '            return self.typeV')
                                codez.insert(21+importOffset, '        # END DEF')
                                codez.insert(22+importOffset, '        def file_lun(self):')
                                codez.insert(23+importOffset, '            return self.file_lunV')
                                codez.insert(24+importOffset, '        # END DEF')
                                codez.insert(25+importOffset, '        def file_offset(self):')
                                codez.insert(26+importOffset, '            return self.file_offsetnV')
                                codez.insert(27+importOffset, '        # END DEF')
                                codez.insert(28+importOffset, '        def n_elements(self):')
                                codez.insert(29+importOffset, '            return self.n_elementsV')
                                codez.insert(30+importOffset, '        # END DEF')
                                codez.insert(31+importOffset, '        def n_dimensions(self):')
                                codez.insert(32+importOffset, '            return self.n_dimensionsV')
                                codez.insert(33+importOffset, '        # END DEF')
                                codez.insert(34+importOffset, '        def dimensions(self):')
                                codez.insert(35+importOffset, '            return self.dimensionsV')
                                codez.insert(36+importOffset, '        # END DEF')
                                codez.insert(37+importOffset, '    # END CLASS')
                                codez.insert(38+importOffset, '    ')
                                codez.insert(39+importOffset, '    # Do what I can')
                                codez.insert(40+importOffset, '    type_name = idl_size_type(var2heck, words=True) # Woo')
                                codez.insert(41+importOffset, '    typey = idl_size_type(var2heck) # Oh yeah')
                                codez.insert(42+importOffset, '    n_elements, n_dimensions, dimensions = idl_size_general( var2heck ) # Call it allll')
                                codez.insert(43+importOffset, '    return fakeStruct(type_nameV=type_name, structure_nameV="", typeV=typey, file_lunV=0, \\')
                                codez.insert(44+importOffset, '        file_offsetnV=0, n_elementsV=n_elements, n_dimensionsV=n_dimensions, dimensionsV=dimensions) # Return something that works somewhat like it is used in IDL')
                                codez.insert(45+importOffset, '# END DEF')
                                codez.insert(46+importOffset, '')
                                
                                importz['np'] = True; # It's needed
                                FLG_FUN_idl_size_structure = True; # It's been added
                            # END IF
                            # Need the idl_size_type function
                            if( FLG_FUN_idl_size_type == False ):
                                # Get cooking
                                codez.insert(0+importOffset, 'def idl_size_type( var2check, words=False ):');
                                codez.insert(1+importOffset, '    if isinstance( var2check, str):');
                                codez.insert(2+importOffset, '        return "string" if words else 7');
                                codez.insert(3+importOffset, '    elif isinstance( var2check, int):');
                                codez.insert(4+importOffset, '        return "long64" if words else 14');
                                codez.insert(5+importOffset, '    elif isinstance( var2check, float):');
                                codez.insert(6+importOffset, '        return "double" if words else 5');
                                codez.insert(7+importOffset, '    elif isinstance( var2check, (np.ndarray, np.generic)):');
                                codez.insert(8+importOffset, '        if var2check == np.bool_:');
                                codez.insert(9+importOffset, '            return "byte" if words else 1');
                                codez.insert(10+importOffset, '        elif var2check == np.int16:');
                                codez.insert(11+importOffset, '            return "int" if words else 2');
                                codez.insert(12+importOffset, '        elif var2check == np.int32:');
                                codez.insert(13+importOffset, '            return "long" if words else 3');
                                codez.insert(14+importOffset, '        elif var2check == np.int64:');
                                codez.insert(15+importOffset, '            return "long64" if words else 14');
                                codez.insert(16+importOffset, '        elif var2check == np.uint16:');
                                codez.insert(17+importOffset, '            return "uint" if words else 12');
                                codez.insert(18+importOffset, '        elif var2check == np.uint32:');
                                codez.insert(19+importOffset, '            return "ulong" if words else 13');
                                codez.insert(20+importOffset, '        elif var2check == np.uint64:');
                                codez.insert(21+importOffset, '            return "ulong64" if words else 15');
                                codez.insert(22+importOffset, '        elif var2check == np.float32:');
                                codez.insert(23+importOffset, '            return "float" if words else 4');
                                codez.insert(24+importOffset, '        elif var2check == np.float64:');
                                codez.insert(25+importOffset, '            return "double" if words else 5');
                                codez.insert(26+importOffset, '        elif var2check == np.complex64:');
                                codez.insert(27+importOffset, '            return "complex" if words else 6');
                                codez.insert(28+importOffset, '        elif var2check == np.complex128:');
                                codez.insert(29+importOffset, '            return "dcomplex" if words else 9');
                                codez.insert(30+importOffset, '        elif var2check == np.int_:');
                                codez.insert(31+importOffset, '            return "long64" if words else 14');
                                codez.insert(32+importOffset, '        elif var2check == np.float_:');
                                codez.insert(33+importOffset, '            return "double" if words else 5');
                                codez.insert(34+importOffset, '        # END IF');
                                codez.insert(35+importOffset, '    elif isinstance( var2check, bool):');
                                codez.insert(36+importOffset, '        return "byte" if words else 1');
                                codez.insert(37+importOffset, '    elif isinstance( var2check, complex):');
                                codez.insert(38+importOffset, '        return "dcomplex" if words else 9');
                                codez.insert(39+importOffset, '    # END IF');
                                codez.insert(40+importOffset, '# END DEF');
                                codez.insert(41+importOffset, '');
                                
                                importz['np'] = True; # It's needed
                                FLG_FUN_idl_size_type = True; # It's been added
                            # END IF
                            # Need the FLG_FUN_idl_size_general function
                            if( FLG_FUN_idl_size_general == False ):
                                # Get cookin
                                codez.insert(0+importOffset, 'def idl_size_general( var2heck, FLG_n_dim=False, FLG_n_elements=False ):')
                                codez.insert(1+importOffset, '    if( isinstance(var2heck, (np.ndarray, np.generic)) ):')
                                codez.insert(2+importOffset, '        n_elements = var2heck.size')
                                codez.insert(3+importOffset, '        n_dimensions = var2heck.ndim')
                                codez.insert(4+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                                codez.insert(5+importOffset, '        shape = var2heck.shape')
                                codez.insert(6+importOffset, '        for i in range(0, len(shape)):')
                                codez.insert(7+importOffset, '            dimensions[i] = shape[i] # Write in as needed')
                                codez.insert(8+importOffset, '        # END FOR i')
                                codez.insert(9+importOffset, '    elif( isinstance(var2heck, (list, tuple)) ): # Worry about recursive later')
                                codez.insert(10+importOffset, '        if( isinstance(var2heck[0], (np.ndarray, np.generic)) ):')
                                codez.insert(11+importOffset, '            print("WARNING in idl_size_struct: List holding numpy array occured, not exactly sure how or what it wants.")')
                                codez.insert(12+importOffset, '            n_elements = 0')
                                codez.insert(13+importOffset, '            for j in range(0, len(var2heck)):')
                                codez.insert(14+importOffset, '                n_elements += var2heck[j].size')
                                codez.insert(15+importOffset, '            # END FOR j')
                                codez.insert(16+importOffset, '            n_dimensions = var2heck[0].ndim # Only look at the 1st, idk this prob won\'t happen')
                                codez.insert(17+importOffset, '            dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                                codez.insert(18+importOffset, '            shape = var2heck[0].shape')
                                codez.insert(19+importOffset, '            for i in range(0, len(shape)):')
                                codez.insert(20+importOffset, '                dimensions[i] = shape[i] # Write in as needed')
                                codez.insert(21+importOffset, '            # END FOR i')
                                codez.insert(22+importOffset, '        else:')
                                codez.insert(23+importOffset, '            n_elements = len(var2heck) # Keep it simple for now')
                                codez.insert(24+importOffset, '            n_dimensions = 1')
                                codez.insert(25+importOffset, '            dimensions = [len(var2heck), 0, 0, 0, 0, 0, 0, 0]')
                                codez.insert(26+importOffset, '        # END IF')
                                codez.insert(27+importOffset, '    else:')
                                codez.insert(28+importOffset, '        # Scalar or string has same, no dims and 1 element')
                                codez.insert(29+importOffset, '        n_elements = 1')
                                codez.insert(30+importOffset, '        n_dimensions = 0')
                                codez.insert(31+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0]')
                                codez.insert(32+importOffset, '    # END IF')
                                codez.insert(33+importOffset, '    if( FLG_n_dim == True ):')
                                codez.insert(34+importOffset, '        return n_dimensions')
                                codez.insert(35+importOffset, '    elif( FLG_n_elements == True ):')
                                codez.insert(36+importOffset, '        return n_dimensions')
                                codez.insert(37+importOffset, '    else:')
                                codez.insert(38+importOffset, '        return n_elements, n_dimensions, dimensions')
                                codez.insert(39+importOffset, '    # END IF')
                                codez.insert(40+importOffset, '# END DEF')
                                codez.insert(41+importOffset, '')
                                
                                importz['np'] = True; # It's needed
                                FLG_FUN_idl_size_general = True; # It's been added
                            # END IF
                            
                            for j in range(i+1, fend):
                                if( regex_avoid_logic(var2check+r' *=', idl[j], skipums) ):
                                    # Variable was re-declared, ditch it
                                    break;
                                # END IF
                                # Requires a . to use the thing, so look for that
                                fixr = 0; # Moves it up so we can escape
                                regexr_var = regex_avoid(var2check+r'\.\w+', idl[j], skipums, stepUp=fixr); # Check for the call
                                while( regexr_var is not None ):
                                    # Ensure the .calls are lower case
                                    idl[j] = strreplace(idl[j], len(var2check)+1+regexr_var.start(), regexr_var.end(), idl[j][len(var2check)+1+regexr_var.start():regexr_var.end()].lower());
                                    fixr = regexr_var.end(); # Escape
                                    
                                    regexr_var = regex_avoid(var2check+r'\.\w+', idl[j], skipums, stepUp=fixr); # Check for the call
                                # END WHILE
                                
                                # # Requires a . to use the thing, so look for that
                                # regexr_var = regex_avoid(var2check+r'\.', idl[j], skipums); # Check for assignment (prob the case)
                                # while( regexr_var is not None ):
                                #     # A few use instances to check
                                #     FLG_match = False; # Catch things that aren't implemented
                                #     regexr_use = regex_avoid(r'\(? *'+var2check+r'.(type|TYPE) *(lt|LT) *4 *\)? *(or|OR) *\(? *'+var2check+r'.(type|TYPE) *(gt|GT) 11 *\)?', idl[j], skipums);
                                #     regexr_use_ne7 = regex_avoid(r'\(? *'+var2check+r'.type +ne +7 *\)?', idl[j].lower(), skipums);
                                #     regexr_use_eq7 = regex_avoid(r'\(? *'+var2check+r'.type +eq +7 *\)?', idl[j].lower(), skipums);
                                #     if( regexr_use is not None ):
                                #         # Means is an int, it is probably a numpy array (if run into a case of NOT, woof I pittyme)
                                #         idl[j] = strreplace( idl[j], regexr_use.start(), regexr_use.end(), 'np.issubdtype('+origVar+'.dtype, np.integer)' );
                                #         FLG_match = True;
                                #         importz['np'] = True; # It's needed
                                #     elif( regexr_use_ne7 is not None ):
                                #         idl[j] = strreplace( idl[j], regexr_use_ne7.start(), regexr_use_ne7.end(), '(not isinstance('+origVar+', str))' );
                                #         FLG_match = True;
                                #     elif( regexr_use_eq7 is not None ):
                                #         idl[j] = strreplace( idl[j], regexr_use_eq7.start(), regexr_use_eq7.end(), 'isinstance('+origVar+', str)' );
                                #         FLG_match = True;
                                #     # END IF
                                    
                                #     if( FLG_match == False ):
                                #         print('size( var, /structure) has non-matching usage! Implement it!')
                                #         breakpoint()
                                #     # END IF
                                #     regexr_var = regex_avoid(var2check+r'\.', idl[j], skipums); # Check for assignment (prob the case)
                                # # END while
                            # END FOR j
                        else:
                            print('non-equals struture size sthing check it, not expected')
                            breakpoint()
                        # END IF
                        # bevItUp = '@NUKETHISLINE'; # Wipe it out, the size structure can be replaced by better stuff
                    elif( regex_avoid_logic(r', */type', bevItUp.lower(), skipums) ):
                        # Write the type code code now
                        regexr_type = regex_avoid(r', */type *\)', bevItUp.lower(), skipums); # Get where we at
                        var2check = bevItUp[regexr.end():regexr_type.start()]; # Get the var to check
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr_type.end(), 'idl_size_type( '+var2check+' )'); # Bazam
                        if( FLG_FUN_idl_size_type == False ):
                            # Get cooking
                            codez.insert(0+importOffset, 'def idl_size_type( var2check, words=False ):');
                            codez.insert(1+importOffset, '    if isinstance( var2check, str):');
                            codez.insert(2+importOffset, '        return "string" if words else 7');
                            codez.insert(3+importOffset, '    elif isinstance( var2check, int):');
                            codez.insert(4+importOffset, '        return "long64" if words else 14');
                            codez.insert(5+importOffset, '    elif isinstance( var2check, float):');
                            codez.insert(6+importOffset, '        return "double" if words else 5');
                            codez.insert(7+importOffset, '    elif isinstance( var2check, (np.ndarray, np.generic)):');
                            codez.insert(8+importOffset, '        if var2check == np.bool_:');
                            codez.insert(9+importOffset, '            return "byte" if words else 1');
                            codez.insert(10+importOffset, '        elif var2check == np.int16:');
                            codez.insert(11+importOffset, '            return "int" if words else 2');
                            codez.insert(12+importOffset, '        elif var2check == np.int32:');
                            codez.insert(13+importOffset, '            return "long" if words else 3');
                            codez.insert(14+importOffset, '        elif var2check == np.int64:');
                            codez.insert(15+importOffset, '            return "long64" if words else 14');
                            codez.insert(16+importOffset, '        elif var2check == np.uint16:');
                            codez.insert(17+importOffset, '            return "uint" if words else 12');
                            codez.insert(18+importOffset, '        elif var2check == np.uint32:');
                            codez.insert(19+importOffset, '            return "ulong" if words else 13');
                            codez.insert(20+importOffset, '        elif var2check == np.uint64:');
                            codez.insert(21+importOffset, '            return "ulong64" if words else 15');
                            codez.insert(22+importOffset, '        elif var2check == np.float32:');
                            codez.insert(23+importOffset, '            return "float" if words else 4');
                            codez.insert(24+importOffset, '        elif var2check == np.float64:');
                            codez.insert(25+importOffset, '            return "double" if words else 5');
                            codez.insert(26+importOffset, '        elif var2check == np.complex64:');
                            codez.insert(27+importOffset, '            return "complex" if words else 6');
                            codez.insert(28+importOffset, '        elif var2check == np.complex128:');
                            codez.insert(29+importOffset, '            return "dcomplex" if words else 9');
                            codez.insert(30+importOffset, '        elif var2check == np.int_:');
                            codez.insert(31+importOffset, '            return "long64" if words else 14');
                            codez.insert(32+importOffset, '        elif var2check == np.float_:');
                            codez.insert(33+importOffset, '            return "double" if words else 5');
                            codez.insert(34+importOffset, '        # END IF');
                            codez.insert(35+importOffset, '    elif isinstance( var2check, bool):');
                            codez.insert(36+importOffset, '        return "byte" if words else 1');
                            codez.insert(37+importOffset, '    elif isinstance( var2check, complex):');
                            codez.insert(38+importOffset, '        return "dcomplex" if words else 9');
                            codez.insert(39+importOffset, '    # END IF');
                            codez.insert(40+importOffset, '# END DEF');
                            codez.insert(41+importOffset, '');
                            
                            importz['np'] = True; # It's needed
                            FLG_FUN_idl_size_type = True; # It's been added
                        # END IF
                        
                        # # Deal case-by-case for now, mimicking the type codes is annoying
                        # regexr_type_ne7 = regex_avoid(r', */type *\) +ne +7', bevItUp.lower(), skipums); # Get where we at
                        # if( regexr_type_ne7 is not None ):
                        #     bevItUp = strreplace(bevItUp, regexr.start(), regexr_type_ne7.end(), ' isinstance('+bevItUp[regexr.end():regexr_type_ne7.start()]+', str)'); # Crunk it
                        # else:
                        #     print('different size($VAR, \type) than seen before:\n'+bevItUp);
                        #     breakpoint();
                        # # END IF        
                    elif( regex_avoid_logic(r', */n_dimen', bevItUp.lower(), skipums) ):
                        regexr_type = regex_avoid(r', */n_dimen *\)', bevItUp.lower(), skipums); # Get where we at
                        var2check = bevItUp[regexr.end():regexr_type.start()]; # Get the var to check
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr_type.end(), 'idl_size_general( '+var2check+', FLG_n_dim=True )'); # Bazam
                        
                        if( FLG_FUN_idl_size_general == False ):
                            # Get cookin
                            codez.insert(0+importOffset, 'def idl_size_general( var2heck, FLG_n_dim=False, FLG_n_elements=False ):')
                            codez.insert(1+importOffset, '    if( isinstance(var2heck, (np.ndarray, np.generic)) ):')
                            codez.insert(2+importOffset, '        n_elements = var2heck.size')
                            codez.insert(3+importOffset, '        n_dimensions = var2heck.ndim')
                            codez.insert(4+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                            codez.insert(5+importOffset, '        shape = var2heck.shape')
                            codez.insert(6+importOffset, '        for i in range(0, len(shape)):')
                            codez.insert(7+importOffset, '            dimensions[i] = shape[i] # Write in as needed')
                            codez.insert(8+importOffset, '        # END FOR i')
                            codez.insert(9+importOffset, '    elif( isinstance(var2heck, (list, tuple)) ): # Worry about recursive later')
                            codez.insert(10+importOffset, '        if( isinstance(var2heck[0], (np.ndarray, np.generic)) ):')
                            codez.insert(11+importOffset, '            print("WARNING in idl_size_struct: List holding numpy array occured, not exactly sure how or what it wants.")')
                            codez.insert(12+importOffset, '            n_elements = 0')
                            codez.insert(13+importOffset, '            for j in range(0, len(var2heck)):')
                            codez.insert(14+importOffset, '                n_elements += var2heck[j].size')
                            codez.insert(15+importOffset, '            # END FOR j')
                            codez.insert(16+importOffset, '            n_dimensions = var2heck[0].ndim # Only look at the 1st, idk this prob won\'t happen')
                            codez.insert(17+importOffset, '            dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                            codez.insert(18+importOffset, '            shape = var2heck[0].shape')
                            codez.insert(19+importOffset, '            for i in range(0, len(shape)):')
                            codez.insert(20+importOffset, '                dimensions[i] = shape[i] # Write in as needed')
                            codez.insert(21+importOffset, '            # END FOR i')
                            codez.insert(22+importOffset, '        else:')
                            codez.insert(23+importOffset, '            n_elements = len(var2heck) # Keep it simple for now')
                            codez.insert(24+importOffset, '            n_dimensions = 1')
                            codez.insert(25+importOffset, '            dimensions = [len(var2heck), 0, 0, 0, 0, 0, 0, 0]')
                            codez.insert(26+importOffset, '        # END IF')
                            codez.insert(27+importOffset, '    else:')
                            codez.insert(28+importOffset, '        # Scalar or string has same, no dims and 1 element')
                            codez.insert(29+importOffset, '        n_elements = 1')
                            codez.insert(30+importOffset, '        n_dimensions = 0')
                            codez.insert(31+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0]')
                            codez.insert(32+importOffset, '    # END IF')
                            codez.insert(33+importOffset, '    if( FLG_n_dim == True ):')
                            codez.insert(34+importOffset, '        return n_dimensions')
                            codez.insert(35+importOffset, '    elif( FLG_n_elements == True ):')
                            codez.insert(36+importOffset, '        return n_dimensions')
                            codez.insert(37+importOffset, '    else:')
                            codez.insert(38+importOffset, '        return n_elements, n_dimensions, dimensions')
                            codez.insert(39+importOffset, '    # END IF')
                            codez.insert(40+importOffset, '# END DEF')
                            codez.insert(41+importOffset, '')
                            
                            importz['np'] = True; # It's needed
                            FLG_FUN_idl_size_general = True; # It's been added
                        # END IF
                    elif( regex_avoid_logic(r', */n_elem', bevItUp.lower(), skipums) ):
                        regexr_type = regex_avoid(r', */n_elem *\)', bevItUp.lower(), skipums); # Get where we at
                        var2check = bevItUp[regexr.end():regexr_type.start()]; # Get the var to check
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr_type.end(), 'idl_size_general( '+var2check+', FLG_n_elements=True )'); # Bazam
                        
                        if( FLG_FUN_idl_size_general == False ):
                            # Get cookin
                            codez.insert(0+importOffset, 'def idl_size_general( var2heck, FLG_n_dim=False, FLG_n_elements=False ):')
                            codez.insert(1+importOffset, '    if( isinstance(var2heck, (np.ndarray, np.generic)) ):')
                            codez.insert(2+importOffset, '        n_elements = var2heck.size')
                            codez.insert(3+importOffset, '        n_dimensions = var2heck.ndim')
                            codez.insert(4+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                            codez.insert(5+importOffset, '        shape = var2heck.shape')
                            codez.insert(6+importOffset, '        for i in range(0, len(shape)):')
                            codez.insert(7+importOffset, '            dimensions[i] = shape[i] # Write in as needed')
                            codez.insert(8+importOffset, '        # END FOR i')
                            codez.insert(9+importOffset, '    elif( isinstance(var2heck, (list, tuple)) ): # Worry about recursive later')
                            codez.insert(10+importOffset, '        if( isinstance(var2heck[0], (np.ndarray, np.generic)) ):')
                            codez.insert(11+importOffset, '            print("WARNING in idl_size_struct: List holding numpy array occured, not exactly sure how or what it wants.")')
                            codez.insert(12+importOffset, '            n_elements = 0')
                            codez.insert(13+importOffset, '            for j in range(0, len(var2heck)):')
                            codez.insert(14+importOffset, '                n_elements += var2heck[j].size')
                            codez.insert(15+importOffset, '            # END FOR j')
                            codez.insert(16+importOffset, '            n_dimensions = var2heck[0].ndim # Only look at the 1st, idk this prob won\'t happen')
                            codez.insert(17+importOffset, '            dimensions = [0, 0, 0, 0, 0, 0, 0, 0] # Prep this thing')
                            codez.insert(18+importOffset, '            shape = var2heck[0].shape')
                            codez.insert(19+importOffset, '            for i in range(0, len(shape)):')
                            codez.insert(20+importOffset, '                dimensions[i] = shape[i] # Write in as needed')
                            codez.insert(21+importOffset, '            # END FOR i')
                            codez.insert(22+importOffset, '        else:')
                            codez.insert(23+importOffset, '            n_elements = len(var2heck) # Keep it simple for now')
                            codez.insert(24+importOffset, '            n_dimensions = 1')
                            codez.insert(25+importOffset, '            dimensions = [len(var2heck), 0, 0, 0, 0, 0, 0, 0]')
                            codez.insert(26+importOffset, '        # END IF')
                            codez.insert(27+importOffset, '    else:')
                            codez.insert(28+importOffset, '        # Scalar or string has same, no dims and 1 element')
                            codez.insert(29+importOffset, '        n_elements = 1')
                            codez.insert(30+importOffset, '        n_dimensions = 0')
                            codez.insert(31+importOffset, '        dimensions = [0, 0, 0, 0, 0, 0, 0, 0]')
                            codez.insert(32+importOffset, '    # END IF')
                            codez.insert(33+importOffset, '    if( FLG_n_dim == True ):')
                            codez.insert(34+importOffset, '        return n_dimensions')
                            codez.insert(35+importOffset, '    elif( FLG_n_elements == True ):')
                            codez.insert(36+importOffset, '        return n_dimensions')
                            codez.insert(37+importOffset, '    else:')
                            codez.insert(38+importOffset, '        return n_elements, n_dimensions, dimensions')
                            codez.insert(39+importOffset, '    # END IF')
                            codez.insert(40+importOffset, '# END DEF')
                            codez.insert(41+importOffset, '')
                            
                            importz['np'] = True; # It's needed
                            FLG_FUN_idl_size_general = True; # It's been added
                        # END IF
                    elif( regex_avoid_logic(r', */tname', bevItUp.lower(), skipums) ):
                        # Write the tname code code now
                        regexr_type = regex_avoid(r', */tname *\)', bevItUp.lower(), skipums); # Get where we at
                        var2check = bevItUp[regexr.end():regexr_type.start()]; # Get the var to check
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr_type.end(), 'idl_size_type( '+var2check+', words=True )'); # Bazam
                        if( FLG_FUN_idl_size_type == False ):
                            # Get cooking
                            codez.insert(0+importOffset, 'def idl_size_type( var2check, words=False ):');
                            codez.insert(1+importOffset, '    if isinstance( var2check, str):');
                            codez.insert(2+importOffset, '        return "string" if words else 7');
                            codez.insert(3+importOffset, '    elif isinstance( var2check, int):');
                            codez.insert(4+importOffset, '        return "long64" if words else 14');
                            codez.insert(5+importOffset, '    elif isinstance( var2check, float):');
                            codez.insert(6+importOffset, '        return "double" if words else 5');
                            codez.insert(7+importOffset, '    elif isinstance( var2check, (np.ndarray, np.generic)):');
                            codez.insert(8+importOffset, '        if var2check == np.bool_:');
                            codez.insert(9+importOffset, '            return "byte" if words else 1');
                            codez.insert(10+importOffset, '        elif var2check == np.int16:');
                            codez.insert(11+importOffset, '            return "int" if words else 2');
                            codez.insert(12+importOffset, '        elif var2check == np.int32:');
                            codez.insert(13+importOffset, '            return "long" if words else 3');
                            codez.insert(14+importOffset, '        elif var2check == np.int64:');
                            codez.insert(15+importOffset, '            return "long64" if words else 14');
                            codez.insert(16+importOffset, '        elif var2check == np.uint16:');
                            codez.insert(17+importOffset, '            return "uint" if words else 12');
                            codez.insert(18+importOffset, '        elif var2check == np.uint32:');
                            codez.insert(19+importOffset, '            return "ulong" if words else 13');
                            codez.insert(20+importOffset, '        elif var2check == np.uint64:');
                            codez.insert(21+importOffset, '            return "ulong64" if words else 15');
                            codez.insert(22+importOffset, '        elif var2check == np.float32:');
                            codez.insert(23+importOffset, '            return "float" if words else 4');
                            codez.insert(24+importOffset, '        elif var2check == np.float64:');
                            codez.insert(25+importOffset, '            return "double" if words else 5');
                            codez.insert(26+importOffset, '        elif var2check == np.complex64:');
                            codez.insert(27+importOffset, '            return "complex" if words else 6');
                            codez.insert(28+importOffset, '        elif var2check == np.complex128:');
                            codez.insert(29+importOffset, '            return "dcomplex" if words else 9');
                            codez.insert(30+importOffset, '        elif var2check == np.int_:');
                            codez.insert(31+importOffset, '            return "long64" if words else 14');
                            codez.insert(32+importOffset, '        elif var2check == np.float_:');
                            codez.insert(33+importOffset, '            return "double" if words else 5');
                            codez.insert(34+importOffset, '        # END IF');
                            codez.insert(35+importOffset, '    elif isinstance( var2check, bool):');
                            codez.insert(36+importOffset, '        return "byte" if words else 1');
                            codez.insert(37+importOffset, '    elif isinstance( var2check, complex):');
                            codez.insert(38+importOffset, '        return "dcomplex" if words else 9');
                            codez.insert(39+importOffset, '    # END IF');
                            codez.insert(40+importOffset, '# END DEF');
                            codez.insert(41+importOffset, '');
                            
                            importz['np'] = True; # It's needed
                            FLG_FUN_idl_size_type = True; # It's been added
                        # END IF
                        regexr_type = regex_avoid(r', */tname *\)[\s\S]+[\'"] *(?:string|byte|int|long64|long|uint|ulong64|ulong|float|double|dcomplex|complex) *[\'"]', bevItUp.lower(), skipums); # Get where we at
                        if( regexr_type is not None ): # Enforce lower case
                            regexr_type = regex_avoid(r'[\'"] *(?:string|byte|int|long64|long|uint|ulong64|ulong|float|double|dcomplex|complex) *[\'"]', bevItUp[:regexr_type.end()].lower(), skipums, stepUp=regexr_type.start()); # Get where we at
                            bevItUp = strreplace(bevItUp, regexr_type.start(), regexr_type.end(), bevItUp[regexr_type.start():regexr_type.end()].lower()); # Bazam
                        # END IF
                    else:
                        regexr_equals = regex_avoid(r'\w+ *=', bevItUp, skipums); # Check for assignment (prob the case)
                        origVar = bevItUp[regexr.end():bevItUp[regexr.end():].find(')')+regexr.end()]; # Get the orig var
                        var2check = bevItUp[regexr_equals.start():regexr_equals.end()-1].rstrip(' ');
                        # Rebuild as needed, typecode of 0 no support for that
                        bevItUp = bevItUp[regexr_equals.start():regexr_equals.end()] + \
                            ' ['+origVar+'.ndim, 0, '+origVar+'.size]';
                        idl.insert(i+1, '[sz.insert(1, shapeDim) for shapeDim in '+origVar+'.shape]'); # Add in a new line for later, it's python
                        fend += 1; # More fend to cover
                    # END IF
                    
                    regexr = regex_avoid(r'size *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # get_kbrd()
                regexr = regex_avoid(r'get_kbrd *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    if( FLG_FUN_idl_wait_key == False ):
                        # Get cooking
                        codez.insert(0+importOffset, 'def wait_key(): #https://stackoverflow.com/a/34956791');
                        codez.insert(1+importOffset, "    ''' Wait for a key press on the console and return it. '''");
                        codez.insert(2+importOffset, '    result = None');
                        codez.insert(3+importOffset, "    if os.name == 'nt':");
                        codez.insert(4+importOffset, '        import msvcrt');
                        codez.insert(5+importOffset, '        result = msvcrt.getwch()');
                        codez.insert(6+importOffset, '    else:');
                        codez.insert(7+importOffset, '        import termios');
                        codez.insert(8+importOffset, '        fd = sys.stdin.fileno()');
                        codez.insert(9+importOffset, '        oldterm = termios.tcgetattr(fd)');
                        codez.insert(10+importOffset, '        newattr = termios.tcgetattr(fd)');
                        codez.insert(11+importOffset, '        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO');
                        codez.insert(12+importOffset, '        termios.tcsetattr(fd, termios.TCSANOW, newattr)');
                        codez.insert(13+importOffset, '        try:');
                        codez.insert(14+importOffset, '            result = sys.stdin.read(1)');
                        codez.insert(15+importOffset, '        except IOError:');
                        codez.insert(16+importOffset, '            pass');
                        codez.insert(17+importOffset, '        finally:');
                        codez.insert(18+importOffset, '            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)');
                        codez.insert(19+importOffset, '    # END IF');
                        codez.insert(20+importOffset, '    return result');
                        codez.insert(21+importOffset, '# END DEF');
                        codez.insert(22+importOffset, '');
                        
                        importz['os'] = True; # It's needed
                        importz['sys'] = True; # It's needed
                        FLG_FUN_idl_wait_key = True; # It's been added
                    # END IF
                    
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end(); # Get the matching parenthesis (so we know where it ends)
                    bevItUp = strreplace(bevItUp, regexr.start(), paren_match, 'wait_key()'); # Bazam
                    
                    regexr = regex_avoid(r'get_kbrd *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                    
                # strcompress
                regexr = regex_avoid(r'strcompress *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    if( FLG_FUN_idl_strcompress == False ):
                        # Get cooking
                        codez.insert(0+importOffset, 'def strcompress(strang, remove_all=False):');
                        codez.insert(1+importOffset, '    if( len(strang) > 0 ):');
                        codez.insert(2+importOffset, '        if( remove_all == False ):');
                        codez.insert(3+importOffset, "            regexr_list = re.findall(r' {2,}', strang); # search only finds the 1st, find as many to deal with unique issues");
                        codez.insert(4+importOffset, '            ');
                        codez.insert(5+importOffset, '            fixr = 0; # Prep fixr');
                        codez.insert(6+importOffset, '            for jk in range(0, len(regexr_list)):');
                        codez.insert(7+importOffset, "                regexr = re.search(r' {2,}', strang[fixr:]); # Watch fixr");
                        codez.insert(8+importOffset, "                strang = strang[0:regexr.start()+fixr]+' '+strang[ regexr.end()+fixr:]; # Replace with one space");
                        codez.insert(9+importOffset, '                fixr += regexr.end(); # Move up');
                        codez.insert(10+importOffset, '            # END FOR jk');
                        codez.insert(11+importOffset, '        else:');
                        codez.insert(12+importOffset, "            strang = strang.replace(' ', ''); # Much easier if remove all");
                        codez.insert(13+importOffset, '        # END IF');
                        codez.insert(14+importOffset, '    # END IF');
                        codez.insert(15+importOffset, '    return strang # Return strang no matter what');
                        codez.insert(16+importOffset, '# END DEF');
                        codez.insert(17+importOffset, '');
                        
                        importz['re'] = True; # It's needed
                        FLG_FUN_idl_strcompress = True; # It's been added
                    # END IF
                    
                    fixr = parenthesis_hunter( bevItUp[regexr.start():] )+regexr.start()+1; # Get the matching parenthesis (so we know where it ends)
                    
                    regexr_removall = regex_avoid(r'/remove_all', bevItUp[:fixr].lower(), skipums, stepUp = regexr.start()); # Regex it
                    if( regexr_removall is not None ):
                        bevItUp = strreplace( bevItUp, regexr_removall.start(), regexr_removall.end(), 'remove_all = True' ); # Replace the bit!
                    # END IF
                    regexr = regex_avoid(r'strcompress *\(', bevItUp.lower(), skipums, stepUp=fixr); # Regex it
                # END WHILE
                
                # fltarr
                regexr = regex_avoid(r'fltarr *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_empty = regex_avoid(r', */nozero', bevItUp.lower(), skipums); # Regex it
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    reals = splitterz( bevItUp[regexr.end():paren_match], ',', splitums );

                    if( regexr_empty is not None ):
                        for jj in range(len(reals)-1, 0, -1):
                            if( '/nozero' in reals[jj] ):
                                reals.pop(jj); # Ditch it
                            # END IF
                        # END FOR jj
                        bevItUp = bevItUp[:regexr.start()]+' np.empty('; # Replace the bit!
                        if( len(reals) == 1 ):
                            bevItUp += reals[0]; # Bam
                        else:
                            bevItUp += '('; # Bam
                            for jj in range(0, len(reals)):
                                bevItUp += reals[jj]+', '; # Build the parenthesis stuff
                            # END FOR jj
                            bevItUp = bevItUp[:-2]+')'; # Bam
                        # END IF
                    else:
                        bevItUp = bevItUp[:regexr.start()]+' np.zeros('; # Replace the bit!
                        if( len(reals) == 1 ):
                            bevItUp += reals[0]; # Bam
                        else:
                            bevItUp += '('; # Bam
                            for jj in range(0, len(reals)):
                                bevItUp += reals[jj]+', '; # Build the parenthesis stuff
                            # END FOR jj
                            bevItUp = bevItUp[:-2]+')'; # Bam
                        # END IF
                    # END IF
                    bevItUp += ', dtype=np.float32)'; # Replace the bit!
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'fltarr *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # intarr
                regexr = regex_avoid(r'intarr *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    regexr_empty = regex_avoid(r', */nozero', bevItUp.lower(), skipums); # Regex it
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    reals = splitterz( bevItUp[regexr.end():paren_match], ',', splitums );

                    if( regexr_empty is not None ):
                        for jj in range(len(reals)-1, 0, -1):
                            if( '/nozero' in reals[jj] ):
                                reals.pop(jj); # Ditch it
                            # END IF
                        # END FOR jj
                        bevItUp = bevItUp[:regexr.start()]+' np.empty('; # Replace the bit!
                        if( len(reals) == 1 ):
                            bevItUp += reals[0]; # Bam
                        else:
                            bevItUp += '('; # Bam
                            for jj in range(0, len(reals)):
                                bevItUp += reals[jj]+', '; # Build the parenthesis stuff
                            # END FOR jj
                            bevItUp = bevItUp[:-2]+')'; # Bam
                        # END IF
                    else:
                        bevItUp = bevItUp[:regexr.start()]+' np.zeros('; # Replace the bit!
                        if( len(reals) == 1 ):
                            bevItUp += reals[0]; # Bam
                        else:
                            bevItUp += '('; # Bam
                            for jj in range(0, len(reals)):
                                bevItUp += reals[jj]+', '; # Build the parenthesis stuff
                            # END FOR jj
                            bevItUp = bevItUp[:-2]+')'; # Bam
                        # END IF
                    # END IF
                    bevItUp += ', dtype=np.int32)'; # Replace the bit!
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'intarr *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # findgen
                regexr = regex_avoid(r'findgen *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    regexr_paren = regex_avoid(r',', bevItUp[regexr.end():paren_match].lower(), skipums); # Regex it
                    if( regexr_paren is not None ):
                        print('ERROR in findgen: havent implemented comma stuff cause I wont till i see it sorry future me')
                        breakpoint()
                    else:
                        bevItUp = strreplace( bevItUp, paren_match, paren_match+1, ', dtype=np.float32)' ); # Replace the bit!
                    # END IF
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.arange(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'findgen *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # dindgen
                regexr = regex_avoid(r'dindgen *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    regexr_paren = regex_avoid(r',', bevItUp[regexr.end():paren_match].lower(), skipums); # Regex it
                    if( regexr_paren is not None ):
                        print('ERROR in dindgen: havent implemented comma stuff cause I wont till i see it sorry future me')
                        breakpoint()
                    else:
                        bevItUp = strreplace( bevItUp, paren_match, paren_match+1, ', dtype=np.float64)' ); # Replace the bit!
                    # END IF
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.arange(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'dindgen *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # replicate
                regexr = regex_avoid(r'replicate *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    reals = splitterz( bevItUp[regexr.end():paren_match], ',', splitums );
                    if( paren_match+1 < len(bevItUp) ):
                        endy = ' '+bevItUp[paren_match+1:]; # Tack on the test if it exists
                    else:
                        endy = ''; # Nothin
                    # END IF
                    bevItUp[paren_match:]
                    if( len(reals) == 2 ):
                        bevItUp = bevItUp[:regexr.start()]+'np.tile( '+reals[0].strip(' ')+', '+reals[1].strip(' ')+' )'+endy; # Replace the bit!
                    else:
                        bevItUp = bevItUp[:regexr.start()]+'np.tile( '+reals[0].strip(' ')+', ('; # Replace the bit!
                        for jj in range(1, len(reals)):
                            bevItUp += reals[jj].strip(' ')+', '; # More
                        # END FOR jj
                        bevItUp = bevItUp[:-2]+' ))'+endy; # Finish it off
                    # END IF
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'replicate *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # total
                regexr = regex_avoid(r'total *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.sum(' ); # Replace the bit!
                    regexr = regex_avoid(r', */double', bevItUp.lower(), skipums); # Regex it
                    if( regexr is not None ):
                        bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ', dtype=np.float64' ); # Replace the bit!
                    # END IF
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'total *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # round
                regexr = regex_avoid(r'round *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.round(' ); # Replace the bit!
                    regexr64 = regex_avoid(r', */l64', bevItUp.lower(), skipums); # Regex it
                    if( regexr64 is not None ):
                        # Tell it to be an int64
                        bevItUp = strreplace( bevItUp, regexr64.start(), regexr64.end(), '' ); # Delete the bit!
                        endparenth = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # Yee (lil dangerous b/c regexr references different length string but I think I don't care
                        bevItUp = strinsert( bevItUp, endparenth, '.astype(np.int64)' );
                    else:
                        # Defaults to be an int32
                        endparenth = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # Yee (lil dangerous b/c regexr references different length string but I think I don't care
                        bevItUp = strinsert( bevItUp, endparenth, '.astype(np.int32)' );
                    # END IF
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'(?<!np\.)round *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # max
                regexr = regex_avoid(r'(?<!np\.)max *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.max(' ); # Replace the bit!
                    regexrM = regex_avoid(r', *min=', bevItUp.lower(), skipums); # Regex it
                    regexrMaxLoc = regex_avoid(r', *\w+ *\)', bevItUp, skipums); # Regex it
                    if( regexrM is not None ):
                        regexrV = regex_avoid(r' *\w+[ +\),]', bevItUp[regexrM.end():], skipums); # Regex it
                        minvar = bevItUp[regexrM.end():][regexrV.start():regexrV.end()].strip(' '); # Get the minimum variable name
                        # Excise the minimum call from the max call
                        bevItUp = bevItUp.replace(bevItUp[regexrM.start():regexrM.end()+regexrV.end()], ''); # Gonezo
                        
                        idl.insert(i+1, minvar+' = '+bevItUp[regexr.start():].replace('np.max(','np.min(')[:bevItUp[regexr.start():].find(';')].strip(' ')); # Add min call on the next line
                        fend += 1; # More fend to cover
                    elif( regexrMaxLoc is not None ):
                        maxLocvar = bevItUp[regexrMaxLoc.start()+1:regexrMaxLoc.end()-1].strip(' '); # Get the minimum variable name
                        # Excise the minimum call from the max call
                        bevItUp = bevItUp.replace(bevItUp[regexrMaxLoc.start():regexrMaxLoc.end()-1], ''); # Gonezo
                        paren_match = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # More magicks
                        
                        idl.insert(i+1, maxLocvar+' = where( '+bevItUp[regexr.start():paren_match]+' == '+bevItUp[regexr.start()+7:paren_match-1].strip(' ')+' )'); # Add where call on the next line
                        idl.insert(i+2, 'if( len( '+maxLocvar+' ) == 1 ) then begin');
                        idl.insert(i+3, maxLocvar+' = '+maxLocvar+'[0]');
                        idl.insert(i+4, 'endif');
                        fend += 4; # More fend to cover
                    # END IF
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'(?<!np\.)max *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # min
                regexr = regex_avoid(r'(?<!np\.)min *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.min(' ); # Replace the bit!
                    regexrM = regex_avoid(r', *max=', bevItUp.lower(), skipums); # Regex it
                    if( regexrM is not None ):
                        regexrV = regex_avoid(r' *\w+[ +\),]', bevItUp[regexrM.end():].lower(), skipums); # Regex it
                        minvar = bevItUp[regexrM.end():][regexrV.start():regexrV.end()].strip(' '); # Get the minimum variable name
                        # Excise the minimum call from the max call
                        bevItUp = bevItUp.replace(bevItUp[regexrM.start():regexrM.end()+regexrV.end()], ''); # Gonezo
                        
                        idl.insert(i+1, minvar+' = '+bevItUp[regexr.start():].replace('np.min(','np.max(')[:bevItUp[regexr.start():].find(';')].strip(' ')); # Add min call on the next line
                        fend += 1; # More fend to cover
                    # END IF
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'(?<!np\.)min *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                            
                # > or < catches (MUST OCCUR BEFORE LT/GT/GE/LE)
                regexrL = regex_avoid_logic(r'[><]', bevItUp, skipums); # Regex it
                while( regexrL == True ):          
                    regexr_double = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp, skipums); # Regex it
                    regexr_single = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp, skipums); # Regex it
                    fixr = 0; # Need it to fix up parentheses sutff
                    if( regexr_double is not None ):
                        # It's a double!
                        # Deal with parentheses that can cause some issues
                        
                        # Figure out the order to apply
                        splitzone_gt = bevItUp[regexr_double.start():regexr_double.end()].find('>')+regexr_double.start(); # Get where the > split occurs
                        splitzone_lt = bevItUp[regexr_double.start():regexr_double.end()].find('<')+regexr_double.start(); # Get where the < split occurs
                        if( splitzone_gt > splitzone_lt ): # This just worries about the order we put stuff in
                            parenz = where_enclosed_parenthesis(bevItUp, splitzone_lt, splitzone_gt);
                            if( parenz is not None ):
                                regexr_single = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp[parenz[0]:parenz[1]], skipums); # Regex it
                                fixr = parenz[0]; # Yee
                            # END IF
                            string2rep = ' np.clip( '+bevItUp[regexr_double.start()+fixr:splitzone_lt].strip(' ')+', '+bevItUp[splitzone_gt+1:regexr_double.end()+fixr].strip(' ')+', '+bevItUp[splitzone_lt+1:splitzone_gt].strip(' ')+' ) '; # This one I guessed
                        else:
                            parenz = where_enclosed_parenthesis(bevItUp, splitzone_gt, splitzone_lt);
                            if( parenz is not None ):
                                regexr_single = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp[parenz[0]:parenz[1]], skipums); # Regex it
                                fixr = parenz[0]; # Yee
                            # END IF
                            string2rep = ' np.clip( '+bevItUp[regexr_double.start()+fixr:splitzone_gt].strip(' ')+', '+bevItUp[splitzone_gt+1:splitzone_lt].strip(' ')+', '+bevItUp[splitzone_lt+1:regexr_double.end()+fixr].strip(' ')+' ) '; # This one should be right
                        # END IF
                        bevItUp = strreplace(bevItUp, regexr_double.start()+fixr, regexr_double.end()+fixr, string2rep); # Replace the bit
                    else:
                        # It's a single!
                        # Figure out which to apply
                        if( bevItUp[regexr_single.start():regexr_single.end()].find('>') > -1 ):
                            # It's greater than
                            splitzone = bevItUp[regexr_single.start():regexr_single.end()].find('>')+regexr_single.start(); # Get where the split occurs
                            # Deal with parentheses that can cause some issues
                            parenz = where_enclosed_parenthesis(bevItUp, splitzone, splitzone);
                            if( parenz is not None ):
                                regexr_single = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp[parenz[0]:parenz[1]], skipums); # Regex it
                                fixr = parenz[0]; # Yee
                            # END IF
                            string2rep = ' np.clip( '+bevItUp[regexr_single.start()+fixr:splitzone].strip(' ')+', '+bevItUp[splitzone+1:regexr_single.end()+fixr].strip(' ')+', None ) ';
                            bevItUp = strreplace(bevItUp, regexr_single.start()+fixr, regexr_single.end()+fixr, string2rep); # Replace the bit
                        else:
                            # It's less than
                            splitzone = bevItUp[regexr_single.start():regexr_single.end()].find('<')+regexr_single.start(); # Get where the split occurs
                            # Deal with parentheses that can cause some issues
                            parenz = where_enclosed_parenthesis(bevItUp, splitzone, splitzone);
                            if( parenz is not None ):
                                regexr_single = regex_avoid(r'[A-Za-z0-9\._+-/*^ \)\(\[\]]+ *[<>] *[A-Za-z0-9\._+-/*^ \)\(\[\]$]+', bevItUp[parenz[0]:parenz[1]], skipums); # Regex it
                                fixr = parenz[0]; # Yee
                            # END IF
                            string2rep = ' np.clip( '+bevItUp[regexr_single.start()+fixr:splitzone].strip(' ')+', None, '+bevItUp[splitzone+1:regexr_single.end()+fixr].strip(' ')+' ) ';
                            bevItUp = strreplace(bevItUp, regexr_single.start()+fixr, regexr_single.end()+fixr, string2rep); # Replace the bit
                        # END IF
                    # END IF
                    importz['np'] = True; # It's needed
                    regexrL = regex_avoid_logic(r'([><])', bevItUp, skipums); # Regex it
                # END WHILE
                                       
                # where
                regexr = regex_avoid(r'where *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    # Check for size request
                    paren_match = parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1; # More magicks
                    regexr_size = regex_avoid(r'(, *\w+ *\)|, *\$\n\s*\w+ *\))$', bevItUp[:paren_match], skipums, FLG_rev=True); # Regex it
                    if( regexr_size is not None ):
                        # Deals with IDL's where( test = test, nSIZE) and nSIZE is the size of the where results
                        comma_size = bevItUp[regexr.start():regexr_size.end()].rfind(',')+regexr.start(); # Deal with this
                        var_size = bevItUp[comma_size+1:regexr_size.end()-1].strip(' '); # Get the var
                        regexr_where = regex_avoid(r'\s*\w+ *=', bevItUp, skipums); # Regex it
                        var_where = bevItUp[regexr_where.start():regexr_where.end()-1].strip('\t').strip(' ')
                        bevItUp = strreplace( bevItUp, comma_size, regexr_size.end(), ')' ); # Replace the bit!
                        # Side step the python<->idl issues
                        if( FLG_FUN_idl_where_size == False ):
                            codez.insert(0+importOffset, 'def idl_where_size( var2heck ): # Gets size of where finds')
                            codez.insert(1+importOffset, '    if( len(var2heck) == 1 ):')
                            codez.insert(2+importOffset, '        var2heck = var2heck[0] # Remove the tuple')
                            codez.insert(3+importOffset, '        var2heck_size = var2heck.size # Size it up directly')
                            codez.insert(4+importOffset, '    else:')
                            codez.insert(5+importOffset, '        var2heck_size = 0 # Prep')
                            codez.insert(6+importOffset, '        for i in range(0, len(var2heck)):')
                            codez.insert(7+importOffset, '            var2heck_size += var2heck[i].size # Add up the sizes')
                            codez.insert(8+importOffset, '        # END FOR i')
                            codez.insert(9+importOffset, '    # END IF')
                            codez.insert(10+importOffset, '    return var2heck_size, var2heck')
                            codez.insert(11+importOffset, '# END DEF')
                            codez.insert(12+importOffset, '')   
                            
                            FLG_FUN_idl_where_size = True;
                        # END IF
                        idl.insert(i+1, '('+var_size+', '+var_where+') = idl_where_size('+var_where+')'); # Add bits on the next line
                        fend += 1; # More fend to cover
                    # END IF
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.where(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    regexr = regex_avoid(r'(?<!np\.)where *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # moment
                regexr = regex_avoid(r'moment *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    relp = bevItUp[regexr.end():paren_match].strip(' '); # Get the var to deal with
                    
                    bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, '( np.mean('+relp+'), np.var('+relp+'), scipy.stats.skew('+relp+'), scipy.stats.kurtosis('+relp+') )' ); # Bazam
                    
                    importz['np'] = True; # It's needed
                    importz['scipy'] = True; # It's needed
                    
                    regexr = regex_avoid(r'moment *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # convol - note, in the rest of the world "convolve" in IDL is "correlate", so "correlate" calls are used to make it ez pz!!!
                regexr = regex_avoid(r'convol *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    relp = bevItUp[regexr.end():paren_match].strip(' '); # Get the var to deal with
                    
                    # Split by comma
                    relp = relp.split(',');
                    
                    # Prep convol-specific flags
                    FLG_conv_type = 'constant'
                    
                    slash_ops = relp[2:]
                    # Slash options here
                    for jj in range(0, len(slash_ops)):
                        if( '/edge_truncate' == slash_ops[jj].lower().replace(' ','') ):
                            FLG_conv_type = 'nearest'
                        else:
                            print('ERROR: Unsupported CONVOL option. Fix it.\n'+slash_ops[jj]);
                            breakpoint(); # Trying this out
                            pass
                        # END IF
                    # END FOR jj
                    
                    if( FLG_conv_type == 'constant' ):
                        # Side step the python<->idl issues
                        if( FLG_FUN_idl_convol == False ):
                            codez.insert(0+importOffset, 'def idl_convol( var2conv, conv_kornel ): # Code that matches what CONVOL does in IDL')
                            codez.insert(6+importOffset, '    var_convd = scipy.signal.correlate(var2conv, conv_kornel, mode=\'valid\')')
                            codez.insert(7+importOffset, '    if( var2conv.shape != var_convd.shape ): # Pad as needed back to original size')
                            codez.insert(8+importOffset, '        pad2pad = np.array(var2conv.shape) - np.array(var_convd.shape)')
                            codez.insert(9+importOffset, '        pad2pad_floor = np.floor(pad2pad/2).astype(np.int64)')
                            codez.insert(10+importOffset, '        pad2pad_ceil = np.ceil(pad2pad/2).astype(np.int64)')
                            codez.insert(11+importOffset, '        var_convd = np.pad(var_convd, ((pad2pad_ceil[0], pad2pad_floor[0]), (pad2pad_ceil[1], pad2pad_floor[1])))')
                            codez.insert(12+importOffset, '    # END IF')
                            codez.insert(13+importOffset, '    return var_convd')
                            codez.insert(14+importOffset, '# END DEF')
                            codez.insert(15+importOffset, '')   
                            
                            FLG_FUN_idl_convol = True;
                        # END IF
                        bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, 'idl_convol('+relp[0]+', '+relp[1]+')' ); # Bazam
                    elif( FLG_conv_type == 'nearest' ):
                        bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, 'scipy.ndimage.correlate('+relp[0]+', '+relp[1]+', mode=\'nearest\')' ); # Bazam
                    # END IF
                    
                    # For testing:
                    # import scipy, numpy as np
                    # array = np.array([ [5, 2.2, 1, 3, 9.5], [9, 2, 6, 6.6, 44], [5, 2, 1, 1, 1], [6, 7, 8, 9, 4.6], [8, 8.1, 2, 4, 3] ])
                    # kernel = np.array([ [0,1,0],[-1,0,1],[0,-1,0] , [1, 1, 1] ])
                    # result = scipy.ndimage.correlate(array, kernel, mode='constant', cval=1.0)
                    # result
                    # # IDL
                    # array = [ [5, 2.2, 1, 3, 9.5], [9, 2, 6, 6.6, 44], [5, 2, 1, 1, 1], [6, 7, 8, 9, 4.6], [8, 8.1, 2, 4, 3] ]
                    # kernel = [ [0,1,0],[-1,0,1],[0,-1,0],[1,1,1] ]
                    # result = CONVOL(array, kernel, /EDGE_CONSTANT)
                    
                    importz['np'] = True; # It's needed
                    importz['scipy'] = True; # It's needed
                    
                    regexr = regex_avoid(r'convol *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # # rot
                # regexr = regex_avoid(r'rot *\(', bevItUp.lower(), skipums); # Regex it
                # while( regexr is not None ):
                #     paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                #     relp = bevItUp[regexr.end():paren_match].strip(' '); # Get the var to deal with
                    
                #     # Split by comma
                #     relp = relp.split(',');
                    
                #     # Prep convol-specific flags
                #     FLG_conv_type = 'constant'
                    
                #     slash_ops = relp[2:]
                #     # Slash options here
                #     for jj in range(0, len(slash_ops)):
                #         if( '/edge_truncate' == slash_ops[jj].lower().replace(' ','') ):
                #             FLG_conv_type = 'nearest'
                #         else:
                #             print('ERROR: Unsupported CONVOL option. Fix it.\n'+slash_ops[jj]);
                #             breakpoint(); # Trying this out
                #             pass
                #         # END IF
                #     # END FOR jj
                    
                #     if( FLG_conv_type == 'constant' ):
                #         # Side step the python<->idl issues
                #         if( FLG_FUN_idl_convol == False ):
                #             codez.insert(0+importOffset, 'def idl_convol( var2conv, conv_kornel ): # Code that matches what CONVOL does in IDL')
                #             codez.insert(6+importOffset, '    var_convd = scipy.signal.correlate(var2conv, conv_kornel, mode=\'valid\')')
                #             codez.insert(7+importOffset, '    if( var2conv.shape != var_convd.shape ): # Pad as needed back to original size')
                #             codez.insert(8+importOffset, '        pad2pad = np.array(var2conv.shape) - np.array(var_convd.shape)')
                #             codez.insert(9+importOffset, '        pad2pad_floor = np.floor(pad2pad/2).astype(np.int64)')
                #             codez.insert(10+importOffset, '        pad2pad_ceil = np.ceil(pad2pad/2).astype(np.int64)')
                #             codez.insert(11+importOffset, '        var_convd = np.pad(var_convd, ((pad2pad_ceil[0], pad2pad_floor[0]), (pad2pad_ceil[1], pad2pad_floor[1])))')
                #             codez.insert(12+importOffset, '    # END IF')
                #             codez.insert(13+importOffset, '    return var_convd')
                #             codez.insert(14+importOffset, '# END DEF')
                #             codez.insert(15+importOffset, '')   
                            
                #             FLG_FUN_idl_convol = True;
                #         # END IF
                #         bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, 'idl_convol('+relp[0]+', '+relp[1]+')' ); # Bazam
                #     elif( FLG_conv_type == 'nearest' ):
                #         bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, 'scipy.ndimage.correlate('+relp[0]+', '+relp[1]+', mode=\'nearest\')' ); # Bazam
                #     # END IF
                    
                #     # import skimage.transform
                #     # im_rotate = skimage.transform.rotate(im_median, 85, center=None, order=3, preserve_range=True)
                    
                #     # For testing:
                #     # import scipy, numpy as np
                #     # array = np.array([ [5, 2.2, 1, 3, 9.5], [9, 2, 6, 6.6, 44], [5, 2, 1, 1, 1], [6, 7, 8, 9, 4.6], [8, 8.1, 2, 4, 3] ])
                #     # kernel = np.array([ [0,1,0],[-1,0,1],[0,-1,0] , [1, 1, 1] ])
                #     # result = scipy.ndimage.correlate(array, kernel, mode='constant', cval=1.0)
                #     # result
                #     # # IDL
                #     # array = [ [5, 2.2, 1, 3, 9.5], [9, 2, 6, 6.6, 44], [5, 2, 1, 1, 1], [6, 7, 8, 9, 4.6], [8, 8.1, 2, 4, 3] ]
                #     # kernel = [ [0,1,0],[-1,0,1],[0,-1,0],[1,1,1] ]
                #     # result = CONVOL(array, kernel, /EDGE_CONSTANT)
                    
                #     importz['np'] = True; # It's needed
                #     importz['scipy'] = True; # It's needed
                #     importz['skimage'] = True; # It's needed
                    
                #     regexr = regex_avoid(r'rot *\(', bevItUp.lower(), skipums); # Regex it
                # # END WHILE
            
                # --- Simple Stuff(TM) ---
                # float
                regexr = regex_avoid(r'float *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.float32(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'float *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # fix
                regexr = regex_avoid(r'fix *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.round(' ); # Replace the bit!
                    # Ensure array is now integers
                    bevItUp = strinsert( bevItUp, parenthesis_hunter(bevItUp[regexr.start():]) + regexr.start() + 1, '.astype(np.int64)');
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'fix *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # finite
                regexr = regex_avoid(r'finite *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.isfinite(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!is)finite *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # sqrt
                regexr = regex_avoid(r'sqrt *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.sqrt(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)sqrt *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # log10
                regexr = regex_avoid(r'alog10 *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.log10(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'alog10 *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # acos
                regexr = regex_avoid(r'acos *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.acos(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)acos *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # asin
                regexr = regex_avoid(r'asin *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.asin(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)asin *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # atan
                regexr = regex_avoid(r'atan *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.atan(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)atan *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # cos
                regexr = regex_avoid(r'(?<!a)cos *\(', bevItUp.lower(), skipums); # Regex it
                fixr = 0;
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.cos('); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    fixr += regexr.end(); # Move it up
                    # regexr = regex_avoid(r'(?<!np\.)cos *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                    regexr = regex_avoid(r'(?<!a)cos *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                # END WHILE
                
                # sin
                regexr = regex_avoid(r'(?<!a)sin *\(', bevItUp.lower(), skipums); # Regex it
                fixr = 0;
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.sin('); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    fixr += regexr.end(); # Move it up
                    # regexr = regex_avoid(r'(?<!np\.)sin *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                    regexr = regex_avoid(r'(?<!a)sin *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                # END WHILE
                
                # tan
                regexr = regex_avoid(r'(?<!a)tan *\(', bevItUp.lower(), skipums); # Regex it
                fixr = 0;
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.tan('); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    fixr += regexr.end(); # Move it up
                    # regexr = regex_avoid(r'(?<!np\.)tan *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                    regexr = regex_avoid(r'(?<!a)tan *\(', bevItUp.lower(), skipums, stepUp = fixr); # Regex it
                # END WHILE
                
                # reverse
                regexr = regex_avoid(r'reverse *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    relp = bevItUp[regexr.end():paren_match].strip(' '); # Get the var to deal with
                    regexr_num = regex_avoid(r', *\d+$', relp, skipums); # Regex it
                    if( regexr_num is not None ):
                        relp_num = str(int(relp[regexr_num.start()+1:regexr_num.end()].replace(' ',''))-1); # Add the skips in, as the reverse in IDL means we don't reverse here on that axis
                        relp = relp[:regexr_num.start()]; # Ditch the number
                    else:
                        relp_num = '0'; # Default to 0 without a number
                    # END IF
                                        
                    strang2replace = 'np.flip('+relp+', axis='+relp_num+')'; # Build the strang to replace
                    
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), strang2replace ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'reverse *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # sort
                regexr = regex_avoid(r'sort *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.sort(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)sort *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # median
                regexr = regex_avoid(r'median *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.median(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)median *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # stddev
                regexr = regex_avoid(r'stddev *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.std(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'stddev *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                               
                # abs
                regexr = regex_avoid(r'abs *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'np.abs(' ); # Replace the bit!
                    importz['np'] = True; # It's needed
                    
                    regexr = regex_avoid(r'(?<!np\.)abs *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # stop
                regexr = regex_avoid(r'^\s*stop(?:[\s;]|$)', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    regexr = regex_avoid(r'stop', bevItUp[:regexr.end()].lower(), skipums, stepUp=regexr.start()); # Regex it
                    
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'breakpoint()' ); # Replace the bit!
                # END WHILE
                                
                # string
                regexr = regex_avoid(r'string *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'str(' ); # Replace the bit!
                    
                    regexr = regex_avoid(r'string *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # repstr
                regexr = regex_avoid(r'repstr *\(', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    paren_match = parenthesis_hunter( bevItUp[regexr.end()-1:] )+regexr.end()-1; # Get the matching parenthesis (so we know where it ends)
                    relp = bevItUp[regexr.end():paren_match].strip(' '); # Get the var to deal with
                    relp = splitterz(relp, ',', splitums); # Split but good
                    
                    bevItUp = strreplace(bevItUp, regexr.start(), paren_match+1, relp[0]+'.replace( '+relp[1]+', '+relp[2]+' )' ); # Bazam
                    regexr = regex_avoid(r'repstr *\(', bevItUp.lower(), skipums); # Regex it
                # END WHILE
            
                # LT
                regexr = regex_avoid(r'(\s+lt\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' < ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'(\s+lt\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # GT
                regexr = regex_avoid(r'(\s+gt\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' > ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'(\s+gt\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # GE
                regexr = regex_avoid(r'(\s+ge\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' >= ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'(\s+ge\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # LE
                regexr = regex_avoid(r'(\s+le\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' <= ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'(\s+le\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # EQ
                regexr = regex_avoid(r'(\s+eq\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' == ' ); # Replace the bit!
               
                    regexr = regex_avoid(r'(\s+eq\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # NE
                regexr = regex_avoid(r'(\s+ne\s+)', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' != ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'(\s+ne\s+)', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                
                # Remove still present / stuff, used as a switch for functions
                regexr = regex_avoid(r', */[a-zA-Z_]+', bevItUp, skipums); # Regex it
                while( regexr is not None ):
                    regexr = regex_avoid(r'/[a-zA-Z_]+', bevItUp[:regexr.end()], skipums, stepUp=regexr.start()); # Regex it
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), bevItUp[regexr.start()+1:regexr.end()]+' = True' ); # Replace the bit!
                    
                    regexr = regex_avoid(r', */[a-zA-Z_]+', bevItUp, skipums); # Regex it
                # END WHILE
                
                # Remove still-present $ stuff
                regexr = regex_avoid(r'\s*\$(\s|\\n|\\t)*', bevItUp.lower(), skipums); # Regex it
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' ' ); # Replace the bit!
                
                    regexr = regex_avoid(r'\s*\$(\s|\\n|\\t)*', bevItUp.lower(), skipums); # Regex it
                # END WHILE
                    
                # end!
                regexrL = regex_avoid_logic(r'^\s*(?:end[ ;]|end$)', bevItUp.lower(), skipums) and strisin( bevItUp.lstrip('\t').lstrip(' ').lower(), 'end', straddlers ); # Regex it
                if( regexrL ):
                    regexr = regex_avoid(r'(\s*end\s*)', bevItUp.lower(), skipums); # Regex it
                    # -- Stuff that needs to happen before the function ends goes here ---
                    if( FLG_plt_gifWriter == True ):
                        codez4later.append('    idl_plt_gifWriter( fig, listFigs ) # Write the gif(s) right before the end of the function (because it has to be done at once not incrementally)');
                    # END IF
                    
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), '; END DEF' ); # Replace the bit!
                    spacer -= 4; # Move everything back NOW
                # END IF
                
                # Look for counting that is wrong cause IDL and Python differ
                # basically gg = findgen(5); gg[2:4] prints 2, 3, 4
                # but for python gg = np.arange(5); gg[2:4] prints 2, 3
                # so ranges need a +1
                # Happens down here to keep other stuff from double dipping
                regexr = regex_avoid(r'\[.*:.*\]', bevItUp, skipums); # Regex it
                fixr = 0; # Lets it waltz forward, because the format doen't change so it just keeps finding the same one
                while( (regexr is not None) and (bevItUp[regexr.start():regexr.end()].replace(' ','') != '[:]') ):
                    bevItUp = strinsert(bevItUp, regexr.end()-1, ' + 1'); # Insert a +1
                    fixr = regexr.end()+3; # I think this is it
                    
                    regexr = regex_avoid(r'\[.*:.*\]', bevItUp, skipums, stepUp = fixr); # Regex it (deals with more in the same line)
                # END WHILE
                
                # Convert else@ to else:, basically it turns out the switch statement uses else: so python'd else: is recorded as else@ to tell the difference!
                regexr = regex_avoid(r'else@', bevItUp.lower(), skipums); # Regex it
                if( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), 'else:' ); # Replace the bit!
                # END IF
                
                # --- Enforce spacing ---
                # If it has real stuff in it, enforce spacer
                regexr = regex_avoid(r'\s{2,}', bevItUp, skipums); # Remove extra spaces
                while( regexr is not None ):
                    bevItUp = strreplace( bevItUp, regexr.start(), regexr.end(), ' ' ); # Replace multi-spaces with space
                    regexr = regex_avoid(r'\s{2,}', bevItUp, skipums); # Remove extra spaces
                # END WHILE
                bevItUp = spacer*' '+bevItUp.lstrip('\t').lstrip(' '); # Space it just right
                
                # --- Dump codez4later to codez ---
                for jk in range(0, len(codez4later)):
                    # These have been built so need less scruitiny, but do need right spacing #python
                    codez.append(' '*spacer+codez4later[jk]); # Blast it on pre-bevItUp
                # END FOR jk
            # END IF
        # END IF
        
        # --- Adjust spacer for future lines ---
        if( FLG_spacer == 1 ):
            spacer += 4; # Move everything up
        elif( FLG_spacer == -1 ):
            spacer -= 4; # Move everything back
        # END IF
        
        # --- Standardize the bevItUp to a list ---
        if( not isinstance(bevItUp, list) ): # After this bevItUp is always a list, makes it easier to target
            bevItUp = [bevItUp]; # Love it or list it
        # END IF
        
        # --- Comment scan ---
        for jk in range(0, len(bevItUp)):
            regexr = regex_avoid(r';', bevItUp[jk], None); # Regex it (implicitly avoids strings)
            if( regexr is not None ):
                bevItUp[jk] = strreplace1( bevItUp[jk], regexr.start(), '#' ); # Replace 1st instance of ;, leave the rest b/c they don't matter
            # END IF
        # END FOR jk
                
        # --- Dump bevItUp to codez ---
        for jk in range(0, len(bevItUp)):
            if( not regex_avoid_logic(r'^\s*@NUKETHISLINE', bevItUp[jk], skipums) ):
                codez.append(bevItUp[jk]); # Append as needed
            # END IF
        # END FOR jk
        
        i += 1; # Increment
    # END WHILE
    
    #!!!
    
    if( any([importz[keyz] for keyz in importz]) ):
        codez.insert(0, ''); # A space to look nice
        for keyz in importz:
            if( importz[keyz] and (keyz == 'np') ):
                codez.insert(0, 'import numpy as np'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'scipy') ):
                codez.insert(0, 'import scipy'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'pd') ):
                codez.insert(0, 'import pandas as pd'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'plt') ):
                codez.insert(0, 'from matplotlib import plot as plt'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'astropy_fits') ):
                codez.insert(0, 'from astropy.io import fits'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'scikit') ):
                codez.insert(0, 'import scikit'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'os') ):
                codez.insert(0, 'import os'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 'sys') ):
                codez.insert(0, 'import sys'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif( importz[keyz] and (keyz == 're') ):
                codez.insert(0, 'import re'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif ( importz[keyz] and (keyz == 'manimation') ):
                codez.insert(0, 'import matplotlib.animation as manimation'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            elif ( importz[keyz] and (keyz == 'pickle') ):
                codez.insert(0, 'import pickle'); # At the top
                importOffset += 1; # Increment the offset (designed to not matter too much here tho)
            else:
                if( importz[keyz] ):
                    print('ERROR: Unsupported import "'+keyz+'" requested. Fix it and crashing.');
                    breakpoint()
                # END IF
            # END IF
        # END FOR keyz
    # END IF
        
    # # --- Fix comments on line continuation, Python does not dig that ---
    # jk = 0; # Rev it up
    # while( jk < len(codez) ):
    #     regexr = regex_avoid(r'#.*\n', codez[jk], None);
    #     while( regexr is not None ):
    #         # Time to move it to the end
    #     # END WHILE
        
    #     jk += 1; # Increment
    # # END WHILE
    
    # --- IDL is more accursed than I ever had dreamt, variables are case insensitive in it, and people actually apply that ---
    # solution is to identify all variables when fully Python'd cause can use Python rules to figure it out
    defLeopard = []; # Prime it
    defJams = []; # Prime it
    for jk in range(0, len(codez)):
        codez[jk]
        if( regex_avoid_logic(r'^\s*def +\w+\(', codez[jk], skipums_py) ):
            defLeopard.append(jk); # Check it out
        # END IF
        if( regex_avoid_logic(r'^\s*# END DEF', codez[jk], None) ):
            defJams.append(jk); # Check it out
        # END IF
    # END FOR jk
    
    # Everything outside the functions needs to be treated as global crap
    # Deal with functions
    for i in range(0, len(defLeopard) ): # Roll through each function
        varDump = []; # Hold the vars here
    
        jk = defLeopard[i]; # While loop so jk shennanigans can occur
        # --- Get vars from the def first ---
        bevItUp = codez[jk]; # Yoink the line
        # --- Detect line continuation, combine ---
        while( end_finder(codez[jk], '\\', skipums_py) ):
            jk += 1; # Increment
            bevItUp += '\n '+codez[jk]; # Tack on more!
        # END WHILE
        jk += 1; # Increment
        endOfDef = jk; # Record for later
        bevItUp = bevItUp.replace('\\\n', ''); # Zap new line stuff
        
        regexr = regex_avoid(r'^\s*def +\w+\(', bevItUp, skipums_py); # Start of function definition
        paren_en = parenthesis_hunter(bevItUp[regexr.end()-1:]) + regexr.end() - 1; # End of function definition
        bevItUp = bevItUp[regexr.end():paren_en].rstrip(' '); # Cut off the ()'s, avoid extra comma from most stuff yeeted except one
        
        bevItUp = bevItUp.split(','); # Consistent syntax means I can do this finally
        for jj in range(0, len(bevItUp) ):
            equy = bevItUp[jj].find('='); # Find that equals
            if( equy > 0 ):
                bevItUp[jj] = bevItUp[jj][:equy]; # Yeet off the rest
            # END IF
            bevItUp[jj] = bevItUp[jj].strip(' ');
            if( bevItUp[jj] != '' ):
                varDump.append(bevItUp[jj]); # Finally got a variable, record it
            # END IF
        # END FOR jj
    
        # --- Get vars from the actual function ---
        try:
            while( jk < defJams[i] ):
                bevItUp = codez[jk]; # Yoink the line
                # --- Detect line continuation, combine ---
                while( end_finder(codez[jk], r'\\', skipums_py) ):
                    jk += 1; # Increment
                    bevItUp += '\n '+codez[jk]; # Tack on more!
                # END WHILE
                bevItUp = bevItUp.replace('\\\n', ''); # Zap new line stuff
                
                # Check for equals, gotta reap
                regexr = regex_avoid(r'(^\s*\w+(?: *, *\w+)* *=(?!=))|(^\s*\( *\w+(?: *, *\w+)* *\)* *=(?!=))', bevItUp, skipums_py)
                if( regexr is not None ):
                    bevItUp = bevItUp[:regexr.end()-1]; # Get the var stuff
                    commy = bevItUp.find(','); # Look for comma
                    if( commy > 0 ):
                        if( bevItUp.find('(') > -1 ):
                            paren_en = parenthesis_hunter(bevItUp); # Look for parenthesis
                            bevItUp = bevItUp[bevItUp.find('(')+1:paren_en]; # Yeet em off
                        # END IF
                        bevItUp = bevItUp.split(','); # Consistent syntax means I can do this finally
                        for jj in range(0, len(bevItUp) ):
                            bevItUp[jj] = bevItUp[jj].strip(' ');
                            varDump.append(bevItUp[jj]); # Finally got a variable, record it
                        # END FOR jj
                    else:
                        # Single defintion, yay
                        varDump.append(bevItUp.strip(' ')); # Finally got a variable, record it
                    # END IF
                # END IF
                jk += 1; # Increment
            # END WHILE
        except:
            breakpoint()
        
        # --- Make them unique and no same var with different case stuff ---
        for jk in range(len(varDump)-1, -1, -1):
            if( any([varDump[jk].lower() == varBoi.lower() for varBoi in varDump[:jk]]) ):
                varDump.pop(jk); # YEET
            # END IF
        # END FOR jk
        
        # --- Make sure none are protected variable names ---
        for jj in range(0, len(varDump)):
            var2check = varDump[jj]; # Check it out
            if( var2check in proctedPy ): # We will be back if someone uses the variable "False" I think, or "None"
                newbie = var2check+'y' ; # Make it not that
                for jk in range(defLeopard[i], defJams[i]): # Go through every line and change it
                    fixr = 0; # Prep the fixr
                    regexr_varCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r'(?:['+straddlersR+r']|$)', codez[jk], skipums_py, stepUp = fixr);
                    while( regexr_varCheck is not None ):
                        # if( regexr_varCheck.start() != 0 ):
                        if( codez[jk][regexr_varCheck.start()] in straddlersR ):
                            sharty = regexr_varCheck.start()+1; # Remove one
                        else:
                            sharty = regexr_varCheck.start(); # Keep cause it's the start
                        # END IF
                        if( codez[jk][regexr_varCheck.end()-1] in straddlersR ):
                            endy = regexr_varCheck.end()-1; # Remove one
                        else:
                            endy = regexr_varCheck.end(); # Keep cause it's the end
                        # END IF
                        
                        regexr_commaCheck= regex_avoid(r'(?:^\s*|else *|then *)'+var2check+r' *,', codez[jk], skipums_py, stepUp = fixr); # Comma stuff gotta start the line, I think
                        regexr_parenCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r' *\(', codez[jk], skipums_py, stepUp = fixr);
                        inParenCheck = where_enclosed_parenthesis(codez[jk], sharty, endy); # Check if in parentheses
                        
                        FLG_noIssue = True; # Good to go by default
                        if( regexr_commaCheck is not None ): # A lot of pomp and circumstance because it can NONE
                            FLG_noIssue = False; # There's an issue
                        # END IF
                        if( regexr_parenCheck is not None ):
                            if( regexr_varCheck.start() == regexr_parenCheck.start() ): # Could match a later one, prevent
                                FLG_noIssue = False; # There's an issue
                            # END IF
                        # END IF
                        if( inParenCheck is not None ):
                            FLG_noIssue = True; # All good lol
                        # END IF
                        if( FLG_noIssue == True ):
                            codez[jk] = strreplace(codez[jk], sharty, endy, newbie); # Make it not var2check
                        # END IF
                        
                        fixr = regexr_varCheck.end(); # Move it up past this one
                        regexr_varCheck = regex_avoid(r'(?:['+straddlersR+r']|^)'+var2check+r'(?:['+straddlersR+r']|$)', codez[jk], skipums_py, stepUp = fixr);
                    # END WHILE
                # END FOR jk
            # END IF
        # END FOR jj
        
        # --- Now make sure the code uses them correctly ---
        for jj in range(0, len(varDump)):
            jk = endOfDef; # Go to the end of the def, don't need to mod the def
            while( jk < defJams[i] ):
                bevItUp = codez[jk]; # Yoink the line
                # --- Detect line continuation, combine ---
                addr = 0; # Important
                while( end_finder(codez[jk], r'\\', skipums_py) ):
                    jk += 1; # Increment
                    addr += 1; # Increment
                    bevItUp += '\n '+codez[jk]; # Tack on more!
                # END WHILE
                # bevItUp = bevItUp.replace('\\\n', ''); # Zap new line stuff
                
                regexr = regex_avoid(varDump[jj].lower(), bevItUp.lower(), skipums_py); # Regex it
                FLG_changed = False; # Flag to help out
                fixr = 0; # Needs this to walk
                while( regexr is not None ):
                    if( strstraddle( bevItUp, regexr.start(), regexr.end(), straddlers ) and (varDump[jj] != bevItUp[regexr.start():regexr.end()]) ):
                        bevItUp = strreplace(bevItUp, regexr.start(), regexr.end(), varDump[jj]); # Make it consistent
                        FLG_changed = True; # Set the flag
                    # END IF
                    fixr = regexr.end(); # Move it up
                    
                    regexr = regex_avoid(varDump[jj].lower(), bevItUp.lower(), skipums_py, stepUp=fixr); # Regex it
                # END WHILE
                if( FLG_changed == True ):
                    bevItUp = bevItUp.split('\n'); # Split on new line
                    if( len(bevItUp) == 1 ):
                        codez[jk] = bevItUp[0]; # Directus
                    else:
                        # Write it in
                        print('ERROR: Never dfealt with this so didnt code it srry write ti now')
                        breakpoint()
                        # for kk in range(0, addr+1):
                        #     bevItUp[kk]
                        # # END FOR kk
                    # END IF
                # END IF
                
                jk += 1; # Increment
            # END WHILE
        # END FOR jj
        
        # --- Replace all placeholder vars now that used vars are known ---
        # Where needs a helper loop, self-contained so choose its var and reuse for all
        varcntr = 0;
        if( 'iter_where' in varDump ):
            while( 'iter_where_'+chr(varcntr + 97) in varDump ):
                varcntr += 1; # Keep going
            # END WHILE
            varpunt = 'iter_where_'+chr(varcntr + 97); # Make it sufficiently unique
        else:
            varpunt = 'iter_where'; # Use it
        # END IF
        varDump.append(varpunt); # Add it on
        # Replace all instances with the chosen unused var
        for jk in range(defLeopard[i], defJams[i]):
            varrep_where = codez[jk].find('!VARR_where!'); # Find it
            if( varrep_where > -1 ):
                codez[jk] = strreplace(codez[jk], varrep_where, varrep_where+12, varpunt); # Replace
            # END IF
        # END FOR jk
        
        # Dynamic loops need unique names too, apply here
        varcntr = 0;
        for jj in range(0, rando_varr_num):
            # Look in the known vars and choose unused vars
            while( 'iterr_'+chr(varcntr + 97) in varDump ):
                varcntr += 1; # Keep going
            # END WHILE
            varpunt = 'iterr_'+chr(varcntr + 97); # Make it sufficiently unique
            varDump.append(varpunt); # Add it on
            
            # Replace all instances with the chosen unused var
            for jk in range(defLeopard[i], defJams[i]):
                varrep_where = codez[jk].find('!VARR_'+str(jj)+'!'); # Find it
                if( varrep_where > -1 ):
                    codez[jk] = strreplace(codez[jk], varrep_where, varrep_where+len('!VARR_'+str(jj)+'!'), varpunt); # Replace
                # END IF
            # END FOR jk
        # END FOR jj
        
    # END FOR i
    
    # Deal with global
    
    
    return codez, defy_report
# END DEF

FLG_validator = False;
FLG_validator_files = ['mmm'];
try:
    fileName = sys.argv[1]
except:
    # fileName = 'fits_add_checksum.pro'
    # fileName = 'mmm.pro'
    # fileName = 'extast.pro'
    # fileName = 'mkhdr.pro'
    fileName = 'rot_gdl.pro'
    # fileName = 'rot_idl.pro'
# END TRYING

try:
    cwd = os.path.dirname(os.path.abspath(fileName)); # Get the directory to work with
except:
    cwd = os.getcwd(); # Backup yolo
# END TRYING
if( os.path.isdir(os.path.join(cwd, 'converted')) == False ):
    os.makedirs(os.path.join(cwd, 'converted'));
# END IF
if( os.path.isdir(os.path.join(cwd, 'converted', 'pylibs')) == False ):
    os.makedirs(os.path.join(cwd, 'converted', 'pylibs'));
# END IF

# --- Read in IDL file ---
with open(fileName, 'r') as file:
    idl = [line.rstrip() for line in file];
# END WITH

# --- Rip into it ---
print('\n--- ON '+fileName+' ---');
convertedCache = {}; # Prep a dict to hold converted functions so you don't have to do it again (need to know what the converted function's analyzed inputs/outputs are so rearrange the line)
codez, _ = trans( idl, libDir = os.path.join(cwd, 'converted', 'pylibs') ); # Translate from IDL to Python (in function form so can recursive if it finds OTHER IDL files)

# --- Save converted Python ---
filePath_conv = os.path.join(cwd, 'converted', fileName.replace('pro','py')); # Put it in a folder
with open(filePath_conv, 'w') as file:
    file.write('\n'.join(linez for linez in codez));
# END WITH

if( FLG_validator == True ):
    print('\n===== VALIDATOR IS ON, VALIDATING =====');
    FLG_good = True; # Assume it's OK
    if( os.path.isdir(os.path.join(cwd, 'validator')) == False ):
        os.makedirs(os.path.join(cwd, 'validator'));
    # END IF
    if( os.path.isdir(os.path.join(cwd, 'validator', 'pylibs')) == False ):
        os.makedirs(os.path.join(cwd, 'validator', 'pylibs'));
    # END IF
    for validator in FLG_validator_files:
        print('--- ON '+validator+'.pro ---');
        
        # --- Read in IDL file ---
        with open(os.path.join(cwd, 'validator', validator+'.pro'), 'r') as file:
            idlT = [line.rstrip() for line in file];
        # END WITH
        
        # --- Rip into it ---
        codezT, _ = trans( idlT, libDir = os.path.join(cwd, 'validator', 'pylibs') ); # Translate from IDL to Python (in function form so can recursive if it finds OTHER IDL files)
        
        # --- Read in reference Python file ---
        with open(os.path.join(cwd, 'validator', validator+'_ref.py'), 'r') as file:
            pyy = [line.rstrip() for line in file];
        # END WITH
        
        
        if( len(codezT) != len(pyy) ):
            print('WARNING: LENGTH DIFFERENT COMPARED TO REFERENCE '+validator+'_ref.py\n');
            FLG_good = False;
        # END IF
        for i in range(0, len(codezT) ):
            if( codezT[i].rstrip(' ') != pyy[i] ):
                print('WARNING: LINE '+str(i)+' DOES NOT MATCH REFERENCE.\nCREATED LINE FOLLOWS:\n'+codezT[i]+'\nREFERENCE LINE FOLLOWS:\n'+pyy[i]+'\n'); # Report issues
                FLG_good = False;
            # END IF
        # END FOR i
    if( FLG_good == True ):
        print('VALIDATION COMPLETE. All good :)');
    else:
        print('VALIDATION COMPLETE. MISMATCHES WERE FOUND. MAY BE REGRESSIONS.');
    # END IF
# END IF

