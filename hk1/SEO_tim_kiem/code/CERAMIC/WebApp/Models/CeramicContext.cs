using Microsoft.EntityFrameworkCore;

namespace WebApp.Models;
public class CeramicContext : DbContext
{
    public CeramicContext(DbContextOptions options) : base(options) {}
    public DbSet<Category> Categories { get; set; }
    public DbSet<Article> Articles { get; set; }
    public DbSet<Member> Members {get; set;}
}
