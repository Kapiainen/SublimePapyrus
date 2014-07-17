using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Text.RegularExpressions;

namespace PapyrusToSublimeSnippets
{
    class Program
    {
        static void Main(string[] args)
        {
            Console.WriteLine("Insert path to directory containing Papyrus source files (defaults to executable's current location, if left empty)\n(example: C:\\Downloads\\skse_1_07_00\\Data\\Scripts\\Source)");
            string SourceDir = Console.ReadLine();
            if (SourceDir.Equals(""))
            {
                SourceDir = Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);
            }
            string OutputDirName = "\\snippets"; //Determines the name of the folder that contains the generated snippets
            StreamWriter funcLog = new StreamWriter(SourceDir + "\\FunctionLog.txt", false);
            StreamWriter classLog = new StreamWriter(SourceDir + "\\ClassLog.txt", false);
            int CountFunctions = 0;
            int CountEvent = 0;
            List<string> SourceSubDirs = new List<string>();
            SourceSubDirs.Add(SourceDir);
            SourceSubDirs.AddRange(Directory.GetDirectories(SourceDir));
            List<string> generatedSnippets = new List<string>(); //Bookkeeping that is used to prevent generating duplicate snippets when processing for example vanilla and SKSE .psc files
            List<string> processedClasses = new List<string>(); //Bookkeeping that is used to prevent multiple entries of the same class in ClassLog.txt
            foreach (string SubDir in SourceSubDirs)
            {
                if (!SubDir.Equals(SourceDir + OutputDirName)) //No need to process output folders
                {
                    string[] files = Directory.GetFiles(SubDir, "*.psc");
                    Console.WriteLine("{0} file(s) found in " + SubDir, files.Length);
                    Regex rx = new Regex(@"(?<=[(|,]\s*)\w+(\[\])?\s+\w+(\s+[=]+\s+\w+)?");
                    Regex EventPattern = new Regex(@"(?i)^\s*\b(event)");
                    Regex FunctionPattern = new Regex(@"(?i)^(\s*\w+\s+)?\b(function)");
                    foreach (string file in files)
                    {
                        string FileName = Path.GetFileNameWithoutExtension(file);
                        StreamReader sr = new StreamReader(file);
                        Console.WriteLine("Working on file: " + FileName);
                        string line;
                        while ((line = sr.ReadLine()) != null)
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
                                string SnippetPattern = FileName + "." + FunctionName; //Determines the name of the generated snippets
                                if (!generatedSnippets.Contains(SnippetPattern)) //If a snippet has been generated for the current function/event, then duplicates shouldn't be generated
                                {
                                    string Parameters = line.Substring(endName, (line.Length - endName));
                                    string OutputDir = SubDir + OutputDirName;
                                    if (!Directory.Exists(OutputDir))
                                    {
                                        Directory.CreateDirectory(OutputDir);
                                    }
                                    StreamWriter sw = new StreamWriter(OutputDir + "\\" + SnippetPattern + ".sublime-snippet", false);
                                    MatchCollection matches = rx.Matches(Parameters);
                                    sw.WriteLine("<snippet>");
                                    sw.WriteLine("\t<tabTrigger>" + FunctionName + "</tabTrigger>");
                                    sw.WriteLine("\t<scope>source.papyrus</scope>");
                                    sw.WriteLine("\t<description>" + FileName + "." + FunctionName + "</description>");
                                    if (EventPattern.IsMatch(line))
                                    {
                                        sw.Write("\t<content><![CDATA[Event " + FunctionName + "(");
                                        int i = 1;
                                        if (matches.Count > 0)
                                        {
                                            foreach (Match match in matches)
                                            {
                                                sw.Write("${" + i + ":" + match + "}");
                                                if (matches[matches.Count - 1] != match)
                                                {
                                                    sw.Write(", ");
                                                }
                                                i++;
                                            }
                                        }
                                        sw.Write(")\n${0}\nEndEvent]]></content>\n");
                                        sw.WriteLine("</snippet>");
                                        CountEvent++;
                                    }
                                    else if (FunctionPattern.IsMatch(line))
                                    {
                                        sw.Write("\t<content><![CDATA[" + FunctionName + "(");
                                        int i = 1;
                                        if (matches.Count > 0)
                                        {
                                            foreach (Match match in matches)
                                            {
                                                sw.Write("${" + i + ":" + match + "}");
                                                if (matches[matches.Count - 1] != match)
                                                {
                                                    sw.Write(", ");
                                                }
                                                i++;
                                            }
                                        }
                                        sw.Write(")]]></content>\n");
                                        sw.WriteLine("</snippet>");
                                        CountFunctions++;
                                    }
                                    funcLog.Write(FunctionName.ToLower() + "|");
                                    sw.Close();
                                    generatedSnippets.Add(FileName + "." + FunctionName); //Adds the generated snippet to the list so that duplicates aren't generated
                                    Console.WriteLine("\t" + SnippetPattern + ".sublime-snippet" + " Created!");
                                }
                            }
                        }
                        if (!processedClasses.Contains(FileName)) //If the class, which is being processed, hasn't been processed earlier, then it can be added to the ClassLog.txt file
                        {
                            classLog.Write(FileName.ToLower() + "|");
                            processedClasses.Add(FileName);
                        }
                        sr.Close();
                    }
                }
            }
            funcLog.Close();
            classLog.Close();
            Console.WriteLine("Created {0} Function-snippets!\nCreated {1} Event-Snippets!", CountFunctions, CountEvent);
            Console.WriteLine("Press a button to close the console...");
            Console.ReadKey();
        }
    }
}
