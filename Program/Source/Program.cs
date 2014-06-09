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
            Console.WriteLine("Insert path to directory containing Papyrus source files (defaults to executable's current location, if left empty)\n(example: C:\\Downloads\\skse_1_07_00\\Data\\scripts\\Source)");
            string PapyrusDir = Console.ReadLine();
            Console.WriteLine("Insert path to output directory (defaults to \"snippets\" subfolder in executable's current location, if left empty)\n(example: C:\\Downloads\\skse_1_07_00\\Data\\scripts\\Source\\out)");
            string OutputDir = Console.ReadLine();
            if (PapyrusDir.Equals(""))
            {
                PapyrusDir = Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location);
            }
            if (OutputDir.Equals(""))
            {
                OutputDir = PapyrusDir + "\\snippets";
            }
            if (!Directory.Exists(OutputDir))
            {
                Directory.CreateDirectory(OutputDir);
            }
            string[] files = Directory.GetFiles(PapyrusDir, "*.psc");
            Console.WriteLine("{0} files found", files.Length);
            int CountFunctions = 0;
            int CountEvent = 0;
            Regex rx = new Regex(@"(?<=[(|,]\s*)\w+(\[\])?\s+\w+(\s+[=]+\s+\w+)?");
            Regex EventPattern = new Regex(@"(?i)^\s*\b(event)");
            Regex FunctionPattern = new Regex(@"(?i)^(\s*\w+\s+)?\b(function)");
            StreamWriter funcLog = new StreamWriter(OutputDir + "\\FunctionLog.txt", false);
            StreamWriter classLog = new StreamWriter(OutputDir + "\\ClassLog.txt", false);
            foreach (string file in files)
            {
                string FileName = Path.GetFileNameWithoutExtension(file);
                StreamReader sr = new StreamReader(file);
                Console.WriteLine("working on file: " + FileName);
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
                        else if(checkingline.Contains("event"))
                        {
                            startName = checkingline.IndexOf("event") + 6;
                        }

                        int endName = line.IndexOf('(');
                        string FunctionName = line.Substring(startName, (endName - startName));
                        string Parameters = line.Substring(endName, (line.Length - endName));
                        StreamWriter sw = new StreamWriter(OutputDir + "\\" + FileName + "." + FunctionName + ".sublime-snippet", false);
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
                        else if(FunctionPattern.IsMatch(line))
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
                        Console.WriteLine("\t" + FileName + "." + FunctionName + ".sublime-snippet" + " Created!");
                    }
                }
                classLog.Write(FileName.ToLower() + "|");
                sr.Close();
            }
            funcLog.Close();
            classLog.Close();
            Console.WriteLine("Created {0} Function-snippets!\nCreated {1} Event-Snippets!", CountFunctions, CountEvent);
            Console.WriteLine("Press a button to close the console...");
            Console.ReadKey();
        }
    }
}
