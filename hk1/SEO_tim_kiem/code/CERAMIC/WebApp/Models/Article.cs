using System.ComponentModel.DataAnnotations.Schema;

namespace WebApp.Models;
[Table("Article")]
public class Article
{
    [Column("ArticleId")]
    public int Id { get; set; }
    public short CategoryId { get; set; }
    public string Title { get; set; } = null!;
    public string Slug { get; set; } = null!;
    public int? Price { get; set; }
    public string Description { get; set; } = null!;
    public string Keywords { get; set; } = null!;
    public string ImageUrl { get; set; } = null!;
    public string Feature { get; set; } = null!;
}