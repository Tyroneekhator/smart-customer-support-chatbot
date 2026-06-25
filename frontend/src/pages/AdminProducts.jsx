import { useEffect, useMemo, useState } from "react";
import { createProduct, getProducts, updateProduct } from "../services/api";

function currency(value) {
  return `£${Number(value || 0).toFixed(2)}`;
}

const EMPTY_FORM = {
  name: "",
  description: "",
  price: "",
  available: true,
};

function AdminProducts() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function loadProducts() {
    setIsLoading(true);
    setError("");

    try {
      const data = await getProducts();
      setProducts(data);
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let shouldIgnore = false;

    async function loadInitialProducts() {
      try {
        const data = await getProducts();

        if (!shouldIgnore) {
          setProducts(data);
        }
      } catch (caughtError) {
        if (!shouldIgnore) {
          setError(caughtError.message);
        }
      } finally {
        if (!shouldIgnore) {
          setIsLoading(false);
        }
      }
    }

    loadInitialProducts();

    return () => {
      shouldIgnore = true;
    };
  }, []);

  const filteredProducts = useMemo(() => {
    const cleanedSearch = searchTerm.toLowerCase().trim();

    return products.filter((product) => {
      const text = [product.name, product.description, product.price]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return !cleanedSearch || text.includes(cleanedSearch);
    });
  }, [products, searchTerm]);

  function handleChange(event) {
    const { name, type, checked, value } = event.target;

    setForm((currentForm) => ({
      ...currentForm,
      [name]: type === "checkbox" ? checked : value,
    }));
  }

  function startEditing(product) {
    setEditingId(product.id);
    setForm({
      name: product.name,
      description: product.description || "",
      price: String(product.price),
      available: product.available,
    });
    setSuccess("");
    setError("");
  }

  function resetForm() {
    setEditingId(null);
    setForm(EMPTY_FORM);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setIsSaving(true);
    setError("");
    setSuccess("");

    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      price: Number(form.price),
      available: form.available,
    };

    if (!payload.name) {
      setError("Product name is required.");
      setIsSaving(false);
      return;
    }

    if (!payload.price || payload.price <= 0) {
      setError("Product price must be greater than 0.");
      setIsSaving(false);
      return;
    }

    try {
      if (editingId) {
        const updatedProduct = await updateProduct(editingId, payload);
        setProducts((currentProducts) =>
          currentProducts.map((product) =>
            product.id === editingId ? updatedProduct : product,
          ),
        );
        setSuccess(`${updatedProduct.name} updated successfully.`);
      } else {
        const newProduct = await createProduct(payload);
        setProducts((currentProducts) => [...currentProducts, newProduct]);
        setSuccess(`${newProduct.name} added successfully.`);
      }

      resetForm();
    } catch (caughtError) {
      setError(caughtError.message);
    } finally {
      setIsSaving(false);
    }
  }

  async function toggleAvailability(product) {
    setError("");
    setSuccess("");

    try {
      const updatedProduct = await updateProduct(product.id, {
        available: !product.available,
      });

      setProducts((currentProducts) =>
        currentProducts.map((currentProduct) =>
          currentProduct.id === product.id ? updatedProduct : currentProduct,
        ),
      );
      setSuccess(
        `${updatedProduct.name} is now ${updatedProduct.available ? "available" : "unavailable"}.`,
      );
    } catch (caughtError) {
      setError(caughtError.message);
    }
  }

  return (
    <main className="admin-page">
      <section className="admin-header">
        <div>
          <p className="eyebrow">Admin Area</p>
          <h1>Product Management</h1>
          <p>Add products, edit prices, and control which products the chatbot can sell.</p>
        </div>

        <div className="admin-actions">
          <button type="button" onClick={loadProducts}>
            Refresh Products
          </button>
        </div>
      </section>

      <section className="admin-grid-two product-admin-grid">
        <article className="admin-panel">
          <h2>{editingId ? "Edit Product" : "Add Product"}</h2>

          <form className="admin-form" onSubmit={handleSubmit}>
            <label>
              Product name
              <input
                type="text"
                name="name"
                value={form.name}
                onChange={handleChange}
                placeholder="Example: Double Chocolate Cookie"
              />
            </label>

            <label>
              Description
              <textarea
                name="description"
                value={form.description}
                onChange={handleChange}
                placeholder="Short product description"
              />
            </label>

            <label>
              Price
              <input
                type="number"
                name="price"
                min="0"
                step="0.01"
                value={form.price}
                onChange={handleChange}
                placeholder="2.50"
              />
            </label>

            <label className="checkbox-label">
              <input
                type="checkbox"
                name="available"
                checked={form.available}
                onChange={handleChange}
              />
              Available for customers
            </label>

            {error && <p className="error-text">{error}</p>}
            {success && <p className="success-text">{success}</p>}

            <div className="form-actions">
              <button type="submit" disabled={isSaving}>
                {isSaving ? "Saving..." : editingId ? "Save Changes" : "Add Product"}
              </button>

              {editingId && (
                <button type="button" className="secondary-button" onClick={resetForm}>
                  Cancel Edit
                </button>
              )}
            </div>
          </form>
        </article>

        <article className="admin-panel">
          <div className="panel-title-row">
            <h2>Current Menu</h2>
            <span>{products.length} products</span>
          </div>

          <label className="full-width-label">
            Search products
            <input
              type="search"
              placeholder="Search by name, description, or price"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
            />
          </label>

          {isLoading ? (
            <p className="status-message">Loading products...</p>
          ) : filteredProducts.length === 0 ? (
            <p className="muted-text">No products found.</p>
          ) : (
            <div className="product-card-list">
              {filteredProducts.map((product) => (
                <div key={product.id} className="product-card">
                  <div>
                    <h3>{product.name}</h3>
                    <p>{product.description || "No description provided."}</p>
                    <strong>{currency(product.price)}</strong>
                  </div>

                  <div className="product-actions">
                    <span className={product.available ? "available-pill" : "unavailable-pill"}>
                      {product.available ? "Available" : "Unavailable"}
                    </span>
                    <button type="button" onClick={() => startEditing(product)}>
                      Edit
                    </button>
                    <button
                      type="button"
                      className="secondary-button"
                      onClick={() => toggleAvailability(product)}
                    >
                      {product.available ? "Hide" : "Show"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </article>
      </section>
    </main>
  );
}

export default AdminProducts;
