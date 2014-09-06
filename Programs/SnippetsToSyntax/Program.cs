using System;
using System.Collections.Generic;
using System.Linq;
using System.IO;

namespace SnippetsToSyntax
{
    class Program
    {
    	static void Main(string[] args)
    	{
    		Console.WriteLine("This program will process Sublime snippets in this folder and the first level of subfolders and add them to the syntax definition in Papyrus.tmLanguge file.");
    		List<string> SourceDirectories = new List<string>();
    		SourceDirectories.Add(Path.GetDirectoryName(System.Reflection.Assembly.GetEntryAssembly().Location));

    		// Check for Papyrus.tmLanguage
    		string[] SyntaxDefinitionCandidates = Directory.GetFiles(SourceDirectories[0], "Papyrus.tmLanguage");
    		if(SyntaxDefinitionCandidates.Length > 0) {
	    		string SyntaxDefinition = SyntaxDefinitionCandidates[0];
	    			//Console.WriteLine("Syntax definition = " + SyntaxDefinition);
	    		if(!SyntaxDefinition.Equals("")) {
	    			// Found Papyrus.tmLanguage, add first level of subdirectories to source directories
		    		SourceDirectories.AddRange(Directory.GetDirectories(SourceDirectories[0]));
		    			//Console.WriteLine("Source directories = " + SourceDirectories.Count());

		    		// Get snippets in all source directories
		    		List<string> Snippets = new List<string>();
		    		foreach (string SourceDir in SourceDirectories) {
		    			Snippets.AddRange(Directory.GetFiles(SourceDir, "*.sublime-snippet"));
		    		}
		    			//Console.WriteLine("Number of files = " + Snippets.Count());

		    		// Process snippets to get class and function/event names for the syntax definition
		    		List<string> Classes = new List<string>();
		    		List<string> Functions = new List<string>();
		    		foreach (string Snippet in Snippets) {
		    			string FileName = Path.GetFileNameWithoutExtension(Snippet).ToLower();
		    				//Console.WriteLine("FileName = " + FileName);
		    			string Class = "";
		    			string Function = "";
		    			int DotIndex = FileName.IndexOf(".");
		    				//Console.WriteLine("DotIndex = " + DotIndex);
		    			if(DotIndex >= 0) {
			    			Class = FileName.Substring(0, DotIndex);
			    			Function = FileName.Substring(FileName.IndexOf(".") + 1);
			    			if(!Classes.Contains(Class)) {
			    				Classes.Add(Class);
			    			}
			    				//Console.WriteLine("Class = " + Class + ", Function = " + Function);
			    		} else {
			    			Function = FileName;
				    			//Console.WriteLine("Function = " + Function);
				    	}
				    	if(!Functions.Contains(Function)) {
				    		Functions.Add(Function);
					    }
		    		}
		    			//Console.WriteLine("Classes = " + Classes.Count() + ", Functions = " + Functions.Count());

		    		// Process Papyrus.tmLanguage
		    		string[] SyntaxLines = File.ReadAllLines(SyntaxDefinition);
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

		    		// Rename original Papyrus.tmLanguage file to Papyrus.tmLanguage.old
		    		string[] OldSyntaxDefinitions = Directory.GetFiles(SourceDirectories[0], "*.tmLanguage.old*");
		    		File.Move(SyntaxDefinition, SyntaxDefinition + ".old" + OldSyntaxDefinitions.Length);
		    		// Create and write new Papyrus.tmLanguage file
		    		File.WriteAllLines(SyntaxDefinition, SyntaxLines);

		    		Console.WriteLine("\nFunction count: " + FunctionCount);
		    		Console.WriteLine("Class count: " + ClassCount);
		    	} else {
		    		Console.WriteLine("Could not find Papyrus.tmLanguage.");
		    	}
		    } else {
		    	Console.WriteLine("Could not find Papyrus.tmLanguage.");
		    }
		    Console.WriteLine("\nPress Enter to exit.");
		    Console.ReadLine();
    	}
    }
}
