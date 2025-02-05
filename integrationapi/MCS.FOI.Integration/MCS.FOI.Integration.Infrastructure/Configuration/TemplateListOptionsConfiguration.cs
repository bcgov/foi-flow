namespace MCS.FOI.Integration.Infrastructure.Configuration
{
    public class TemplateListOptionsConfiguration : IEntityTypeConfiguration<TemplateListOptions>
    {
        public void Configure(EntityTypeBuilder<TemplateListOptions> builder)
        {
            builder.HasKey(b => b.Id);

            builder.HasIndex(b => new { b.Id })
                .IsUnique();

            builder.Property(b => b.Code)
                .HasColumnType("varchar(100)")
                .IsRequired();

            builder.Property(b => b.Description)
                .HasColumnType("varchar(1000)")
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
        }
    }
}
