namespace MCS.FOI.Integration.Infrastructure.Extensions
{
    public static class DataMigration
    {
        private static readonly Assembly _assembly = Assembly.GetAssembly(typeof(DataMigration));

        /// <summary>
        /// Executes SQL from a file, either embedded or external.
        /// </summary>
        /// <param name="migrationBuilder">The MigrationBuilder instance.</param>
        /// <param name="path">The path to the SQL file (embedded or external).</param>
        /// <param name="isEmbedded">Indicates if the file is embedded in the assembly.</param>
        /// <param name="suppressTransaction">Indicates if the SQL should be executed outside of a transaction.</param>
        public static void SqlFromFile(this MigrationBuilder migrationBuilder, string path, bool isEmbedded = true, bool suppressTransaction = false)
        {
            string sqlContent;

            if (isEmbedded)
            {
                using var stream = _assembly.GetManifestResourceStream($"{_assembly.GetName().Name}.{path}");
                if (stream == null)
                    throw new FileNotFoundException($"Resource file '{path}' not found in the assembly '{_assembly.GetName().Name}'.");

                using var reader = new StreamReader(stream);
                sqlContent = reader.ReadToEnd();
            }
            else
            {
                if (!File.Exists(path))
                    throw new FileNotFoundException($"File '{path}' not found.");

                sqlContent = File.ReadAllText(path);
            }

            Console.WriteLine($"Executing SQL script: {path}");
            migrationBuilder.Sql(sqlContent, suppressTransaction);
        }

        /// <summary>
        /// Executes a seed script from the embedded resources.
        /// </summary>
        /// <param name="migrationBuilder">The MigrationBuilder instance.</param>
        /// <param name="scriptName">The name of the script without the extension.</param>
        public static void SeedOrUpdateDatabaseScripts(this MigrationBuilder migrationBuilder, string scriptName)
        {
            migrationBuilder.SqlFromFile($"Data.{scriptName}.sql");
        }
    }
}
