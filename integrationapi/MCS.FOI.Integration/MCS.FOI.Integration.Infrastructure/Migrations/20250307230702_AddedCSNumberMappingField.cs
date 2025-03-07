using MCS.FOI.Integration.Infrastructure.Extensions;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace MCS.FOI.Integration.Infrastructure.Migrations
{
    /// <inheritdoc />
    public partial class AddedCSNumberMappingField : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            DataMigration.SeedOrUpdateDatabaseScripts(migrationBuilder, "InsertAddTemplateFieldMapping");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {

        }
    }
}
