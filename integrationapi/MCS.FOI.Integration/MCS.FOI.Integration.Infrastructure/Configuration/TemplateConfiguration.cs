namespace MCS.FOI.Integration.Infrastructure.Configuration
{
    public class TemplateConfiguration: IEntityTypeConfiguration<Template>
    {
        public void Configure(EntityTypeBuilder<Template> builder)
        {
            builder.HasKey(b => b.Id);

            builder.HasIndex(b => new { b.Id, b.FileName })
                .IsUnique();

            builder.Property(b => b.TemplateName)
                .HasColumnType("varchar(250)")
                .IsRequired();

            builder.Property(b => b.FileName)
                .HasColumnType("varchar(250)")
                .IsRequired();

            builder.Property(b => b.Extension)
                .HasColumnType("varchar(10)")
                .IsRequired();

            builder.Property(b => b.RequestType)
                .HasColumnType("varchar(20)")
                .IsRequired();

            builder.Property(b => b.DocumentPath)
                .HasColumnType("varchar(250)")
                .IsRequired();

            builder.Property(b => b.EncodedContent)
                .HasColumnType("nvarchar(max)");

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
