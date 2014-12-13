using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Text.RegularExpressions;

namespace SublimePapyrus
{
    class Program
    {
        const int OPTION_CANCEL = 0;
        const int OPTION_GENERATESNIPPETS = 1;
        const int OPTION_UPDATESYNTAXHIGHLIGHTING = 2;
        const int OPTION_EVERYTHING = 3;
        const string OUTPUT_SNIPPETSUBFOLDER = "Snippets";
        const string FILE_SNIPPETEXTENSION = ".sublime-snippet";
        const string FILE_SOURCEEXTENSION = ".psc";
        const string FILE_LANGUAGEDEFINITION = "Papyrus.tmLanguage";
        const string FILE_LIBRARYDESCRIPTION = "Description.txt";

        static bool OS_UNIX = false;

        static void Main(string[] args)
        {
            // Check the OS that this binary is being executed on in order to use the correct format for paths.
            OperatingSystem OS = Environment.OSVersion;
            PlatformID PID = OS.Platform;
            switch(PID)
            {
                case PlatformID.Win32NT:
                case PlatformID.Win32Windows:
                case PlatformID.Win32S:
                case PlatformID.WinCE:
                    break;
                case PlatformID.Unix:
                    OS_UNIX = true;
                    break;
                default:
                    Console.WriteLine("Running on unidentified (possibly incompatible) OS.\n");
                    break;
            }

            // Display options available to the user.
            Console.WriteLine("Welcome to SublimePapyrus.");
            int iOption = -1;
            bool bRepeat = true;
            while(bRepeat)
            {
                Console.WriteLine("Choose what you would like to do:");
                Console.WriteLine("{0}. Generate snippets from .psc files.", OPTION_GENERATESNIPPETS);
                Console.WriteLine("{0}. Update syntax highlighting from .sublime-snippet files.", OPTION_UPDATESYNTAXHIGHLIGHTING);
                Console.WriteLine("{0}. Do everything above in order.", OPTION_EVERYTHING);
                Console.WriteLine("{0}. Cancel.\n", OPTION_CANCEL);
                string sInput = Console.ReadLine();
                Console.Clear();
                try
                {
                    iOption = Convert.ToInt32(sInput);
                }
                catch(FormatException e)
                {
                    Console.WriteLine("No digits found in input.");
                }
                finally
                {
                    if(iOption < Int32.MaxValue)
                    {
                        if((iOption >= OPTION_CANCEL) && (iOption <= OPTION_EVERYTHING))
                        {
                            bRepeat = false;
                        } else {
                            Console.WriteLine("Invalid input. Try again.\n");
                        }
                        
                    }
                    else
                    {
                        Console.WriteLine("Input cannot be stored as Int32.");
                    }
                }
            }

            // Non-cancel option was selected.
            if(iOption > OPTION_CANCEL)
            {
                // Get the folder to process.
                string sParentFolder = "";
                for(int i = 0; i < args.Length; i++)
                {
                    if(Directory.Exists(args[i]))
                    {
                        sParentFolder = args[i];
                        break;
                    }
                }

                if(sParentFolder.Equals(""))
                {
                    sParentFolder = getParentFolder();
                }
                Console.Clear();

                // Generate snippets.
                if((iOption == OPTION_EVERYTHING) || (iOption == OPTION_GENERATESNIPPETS))
                {
                    List<string> lsSourceFiles = new List<string>();
                    lsSourceFiles.AddRange(Directory.GetFiles(sParentFolder, ("*" + FILE_SOURCEEXTENSION), System.IO.SearchOption.AllDirectories));

                    generateSnippets(lsSourceFiles);

                    if(iOption == OPTION_EVERYTHING)
                    {
                        Console.WriteLine("\nPress a button to continue.");
                        Console.ReadKey();
                        Console.Clear();
                    }
                }

                // Update syntax highlighting.
                if((iOption == OPTION_EVERYTHING) || (iOption == OPTION_UPDATESYNTAXHIGHLIGHTING))
                {
                    // Look for Papyrus.tmLanguage.
                    List<string> lsLanguageDefinitions = new List<string>();
                    lsLanguageDefinitions.AddRange(Directory.GetFiles(sParentFolder, FILE_LANGUAGEDEFINITION, System.IO.SearchOption.AllDirectories));

                    if(lsLanguageDefinitions.Count > 0)
                    {
                        int iLanguageDefinition = 0;
                        if(lsLanguageDefinitions.Count > 1)
                        {
                            bRepeat = true;
                            while(bRepeat)
                            {
                                Console.WriteLine("Found {0} copies of " + FILE_LANGUAGEDEFINITION + ".\nSelect the one you want to use by inputting the corresponding index:", lsLanguageDefinitions.Count);
                                for(int i = 0; i < lsLanguageDefinitions.Count; i++)
                                {
                                    Console.WriteLine("{0}. '" + lsLanguageDefinitions[i] + "'", i);
                                }
                                string sInput = Console.ReadLine();
                                try
                                {
                                    iLanguageDefinition = Convert.ToInt32(sInput);
                                }
                                catch(FormatException e)
                                {
                                    Console.WriteLine("No digits found in input.");
                                }
                                finally
                                {
                                    if(iLanguageDefinition < Int32.MaxValue)
                                    {
                                        if((iLanguageDefinition >= 0) && (iLanguageDefinition < lsLanguageDefinitions.Count))
                                        {
                                            bRepeat = false;
                                        } else {
                                            Console.WriteLine("Invalid input. Try again.\n");
                                        }
                                        
                                    }
                                    else
                                    {
                                        Console.WriteLine("Input cannot be stored as Int32.");
                                    }
                                }

                            }
                        }

                        // Look for snippets.
                        List<string> lsSnippets = new List<string>();
                        lsSnippets.AddRange(Directory.GetFiles(sParentFolder, ("*" + FILE_SNIPPETEXTENSION), System.IO.SearchOption.AllDirectories));

                        if(lsSnippets.Count > 0)
                        {
                            updateSyntaxHighlighting(lsLanguageDefinitions[iLanguageDefinition], lsSnippets);
                        }
                        else
                        {
                            Console.WriteLine("Could not find any " + FILE_SNIPPETEXTENSION + " files.");
                        }
                    }
                    else
                    {
                        Console.WriteLine("Could not find a copy of " + FILE_LANGUAGEDEFINITION + ".");
                    }
                }

                Console.WriteLine("\nPress a button to close the program.");
                Console.ReadKey();
            }
        }

        static string getParentFolder()
        {
            Console.WriteLine("Insert path to directory you wish to process or leave empty to use the directory that this executable is in.\n");
            if(OS_UNIX)
            {
                Console.WriteLine("Example: ~/Documents/Papyrus Source Files");
            }
            else
            {
                Console.WriteLine("Example: C:\\Papyrus Source Files");
            }
            string sParentFolder = Console.ReadLine();
            if(sParentFolder.Equals(""))
            {
                sParentFolder = Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);
            }
            return sParentFolder;
        }

        static void generateSnippets(List<string> alsSourceFiles)
        {
            Regex rx = new Regex(@"(?<=[(|,]\s*)\w+(\[\])?\s+\w+(\s+[=]+\s+\w+)?");
            Regex EventPattern = new Regex(@"(?i)^\s*\b(event)");
            Regex FunctionPattern = new Regex(@"(?i)^(\s*\w+\s+)?\b(function)");
            int CountEvent = 0;
            int CountFunctions = 0;
            List<string> generatedSnippets = new List<string>(); //Bookkeeping that is used to prevent generating duplicate snippets when processing for example vanilla and SKSE .psc files.

            for(int i = 0; i < alsSourceFiles.Count; i++)
            {
                string FileName = Path.GetFileNameWithoutExtension(alsSourceFiles[i]);

                // Get the optional library description.
                string[] DescriptionPath;
                if (OS_UNIX) 
                {
                    DescriptionPath = Directory.GetFiles(alsSourceFiles[i].Substring(0, alsSourceFiles[i].LastIndexOf("/")), FILE_LIBRARYDESCRIPTION);
                } else {
                    DescriptionPath = Directory.GetFiles(alsSourceFiles[i].Substring(0, alsSourceFiles[i].LastIndexOf("\\")), FILE_LIBRARYDESCRIPTION);
                }
                string Description = "";
                if (DescriptionPath.Length > 0) 
                {
                    using (StreamReader srDescription = new StreamReader(DescriptionPath[0]))
                    {
                        string lineDescription;
                        while ((lineDescription = srDescription.ReadLine()) != null)
                        {
                            Description = lineDescription;
                            break;
                        }
                    }
                }

                StreamReader sr = new StreamReader(alsSourceFiles[i]);
                Console.WriteLine("\nWorking on file: " + FileName);
                string line;
                bool skipLine = false; //Keeps track of whether or not a comment block is being processed.
                while ((line = sr.ReadLine()) != null)
                {
                    if (!skipLine)
                    {
                        if (line.Contains(";/"))
                        {
                            //Comment block has started, so we can disregard all lines from here on until the comment block ends.
                            skipLine = true;
                        }
                        else
                        {
                            if (EventPattern.IsMatch(line) || FunctionPattern.IsMatch(line))
                            {
                                string checkingline = line.ToLower();
                                int startName = 0;
                                if (checkingline.Contains("function"))
                                {
                                    startName = checkingline.IndexOf("function") + 9;
                                }
                                else if (checkingline.Contains("event"))
                                {
                                    startName = checkingline.IndexOf("event") + 6;
                                }

                                int endName = line.IndexOf('(');
                                string FunctionName = line.Substring(startName, (endName - startName));
                                string SnippetPattern = FileName + "." + FunctionName; //Determines the name of the generated snippets.
                                if (!generatedSnippets.Contains(SnippetPattern)) //If a snippet has been generated for the current function/event, then duplicates shouldn't be generated.
                                {
                                    string Parameters = line.Substring(endName, (line.Length - endName));

                                    // Check if parameters are spread across multiple lines
                                    while (Parameters.Contains('\\'))
                                    {
                                        Parameters = Parameters.Substring(0, (Parameters.IndexOf('\\') - 1));
                                        string nextLine = sr.ReadLine();
                                        Parameters += nextLine;
                                    }

                                    // Set the output directory.
                                    string OutputDir;
                                    if(OS_UNIX)
                                    {
                                        OutputDir = Path.GetDirectoryName(alsSourceFiles[i]) + "/" + OUTPUT_SNIPPETSUBFOLDER;
                                    }
                                    else
                                    {
                                        OutputDir = Path.GetDirectoryName(alsSourceFiles[i]) + "\\" + OUTPUT_SNIPPETSUBFOLDER;
                                    }

                                    if (!Directory.Exists(OutputDir))
                                    {
                                        Directory.CreateDirectory(OutputDir);
                                    }

                                    // Create and write the snippet.
                                    StreamWriter sw;
                                    if(OS_UNIX)
                                    {
                                        sw = new StreamWriter(OutputDir + "/" + SnippetPattern + FILE_SNIPPETEXTENSION, false);
                                    }
                                    else
                                    {
                                        sw = new StreamWriter(OutputDir + "\\" + SnippetPattern + FILE_SNIPPETEXTENSION, false);
                                    }
                                    MatchCollection matches = rx.Matches(Parameters);
                                    sw.WriteLine("<snippet>");
                                    sw.WriteLine("\t<tabTrigger>" + FunctionName + "</tabTrigger>");
                                    sw.WriteLine("\t<scope>source.papyrus</scope>");
                                    if (!Description.Equals("")) 
                                    {
                                        sw.WriteLine("\t<description>" + FileName + "." + FunctionName + " (" + Description + ")</description>");
                                    } else {
                                        sw.WriteLine("\t<description>" + FileName + "." + FunctionName + "</description>");
                                    }
                                    if (EventPattern.IsMatch(line))
                                    {
                                        sw.Write("\t<content><![CDATA[Event " + FunctionName + "(");
                                        int j = 1;
                                        if (matches.Count > 0)
                                        {
                                            foreach (Match match in matches)
                                            {
                                                sw.Write("${" + j + ":" + match + "}");
                                                if (matches[matches.Count - 1] != match)
                                                {
                                                    sw.Write(", ");
                                                }
                                                j++;
                                            }
                                        }
                                        sw.Write(")\n${0}\nEndEvent]]></content>\n");
                                        CountEvent++;
                                    }
                                    else if (FunctionPattern.IsMatch(line))
                                    {
                                        sw.Write("\t<content><![CDATA[" + FunctionName + "(");
                                        int j = 1;
                                        if (matches.Count > 0)
                                        {
                                            foreach (Match match in matches)
                                            {
                                                sw.Write("${" + j + ":" + match + "}");
                                                if (matches[matches.Count - 1] != match)
                                                {
                                                    sw.Write(", ");
                                                }
                                                j++;
                                            }
                                        }
                                        sw.Write(")]]></content>\n");
                                        CountFunctions++;
                                    }
                                    sw.WriteLine("</snippet>");
                                    sw.Close();

                                    generatedSnippets.Add(SnippetPattern); //Adds the generated snippet to the list so that duplicates aren't generated.
                                    Console.WriteLine("\t" + SnippetPattern + FILE_SNIPPETEXTENSION + " Created!"); 
                                }
                            }
                        }
                    }
                    else
                    {
                        if (line.Contains("/;"))
                        {
                            // The comment block has ended, so we need to process the next line.
                            skipLine = false;
                        }
                    }
                }
                sr.Close();
            }

            Console.WriteLine("Created {0} function snippets!\nCreated {1} event snippets!", CountFunctions, CountEvent);
        }

        static void updateSyntaxHighlighting(string asLanguageDefinition, List<string> alsSnippets)
        {
            // Process snippets to get class and function/event names for the syntax definition
            List<string> Classes = new List<string>();
            List<string> Functions = new List<string>();
            foreach (string Snippet in alsSnippets) {
                string FileName = Path.GetFileNameWithoutExtension(Snippet).ToLower();
                string Class = "";
                string Function = "";
                int DotIndex = FileName.IndexOf(".");
                if(DotIndex >= 0) {
                    Class = FileName.Substring(0, DotIndex);
                    Function = FileName.Substring(FileName.IndexOf(".") + 1);
                    if(!Classes.Contains(Class)) {
                        Classes.Add(Class);
                    }
                } else {
                    Function = FileName;
                }
                if(!Functions.Contains(Function)) {
                    Functions.Add(Function);
                }
            }

            // Process Papyrus.tmLanguage
            string[] SyntaxLines = File.ReadAllLines(asLanguageDefinition);
            // Find the and replace function syntax line
            int FunctionLineIndex = -1;
            for(int i = 0; i < SyntaxLines.Length; i++) {
                if(SyntaxLines[i].Contains("support.function.papyrus")) {
                    FunctionLineIndex = i - 2;
                    break;
                }
            }
            int FunctionCount = Functions.Count();
            string FunctionLine = "";
            Console.WriteLine("\nFunctions in syntax:");
            for(int i = 0; i < FunctionCount; i++) {
                Console.WriteLine("- " + Functions[i]);
                FunctionLine += Functions[i];
                if(i < (FunctionCount - 1)) {
                    FunctionLine += "|";
                }
            }
            SyntaxLines[FunctionLineIndex] = "            <string>(?i)\\b(" + FunctionLine + ")\\b</string>";

            // Find and replace the class syntax line
            int ClassLineIndex = -1;
            for(int i = 0; i < SyntaxLines.Length; i++) {
                if(SyntaxLines[i].Contains("support.class.papyrus")) {
                    ClassLineIndex = i - 2;
                    break;
                }
            }
            int ClassCount = Classes.Count();
            string ClassLine = "";
            Console.WriteLine("\nClasses in syntax:");
            for(int i = 0; i < ClassCount; i++) {
                Console.WriteLine("- " + Classes[i]);
                ClassLine += Classes[i];
                if(i < (ClassCount - 1)) {
                    ClassLine += "|";
                }
            }
            SyntaxLines[ClassLineIndex] = "            <string>(?i)\\b(" + ClassLine + ")\\b</string>";

            string[] OldSyntaxDefinitions = Directory.GetFiles(Path.GetDirectoryName(asLanguageDefinition), (FILE_LANGUAGEDEFINITION + ".old*")); // Find old syntax definitions
            File.Move(asLanguageDefinition, asLanguageDefinition + ".old" + OldSyntaxDefinitions.Length); // Rename original Papyrus.tmLanguage file to Papyrus.tmLanguage.old#
            File.WriteAllLines(asLanguageDefinition, SyntaxLines); // Create and write a new Papyrus.tmLanguage file

            Console.WriteLine("\nFunction count: " + FunctionCount);
            Console.WriteLine("Class count: " + ClassCount);
        }
    }
}
