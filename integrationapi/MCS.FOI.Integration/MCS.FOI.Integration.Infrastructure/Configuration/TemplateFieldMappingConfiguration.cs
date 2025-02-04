namespace MCS.FOI.Integration.Infrastructure.Configuration
{
    public class TemplateFieldMappingConfiguration : IEntityTypeConfiguration<TemplateFieldMapping>
    {
        public void Configure(EntityTypeBuilder<TemplateFieldMapping> builder)
        {
            builder.HasKey(b => b.Id);

            builder.HasIndex(b => new { b.Id })
                .IsUnique();

            builder.Property(b => b.FieldName)
                .HasColumnType("varchar(250)")
                .IsRequired();

            builder.Property(b => b.FieldType)
                .HasColumnType("varchar(20)")
                .IsRequired();

            builder.Property(a => a.CreatedAt)
                .HasColumnType("timestamp")
                .HasDefaultValueSql("NOW()");

            builder.Property(b => b.CreatedBy)
                .HasColumnType("varchar(120)")
                .IsRequired(false); // Nullable;

            builder.Property(b => b.UpdatedBy)
                .HasColumnType("varchar(120)")
                .IsRequired(false); // Nullable;

            builder.Property(b => b.IsActive)
                .HasDefaultValue(true);
        }
    }
}
