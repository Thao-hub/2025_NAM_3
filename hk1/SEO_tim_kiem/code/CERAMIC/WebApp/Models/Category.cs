using System.ComponentModel.DataAnnotations.Schema;

namespace WebApp.Models;
[Table("Category")]
public class Category
{
    [Column("CategoryID")]
    public short Id { get; set; }
    [Column("CategoryName")]
    public string Name { get; set; } = null!;
    public string Slug { get; set; } = null!;
    public string Heading { get; set; } = null!;
    public string ImageUrl { get; set; } = null!;
    public string Description { get; set; } = null!;
    public string Introduction { get; set; } = null!;
    public string Content { get; set; } = null!;
}