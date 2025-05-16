use postgres::types::{FromSql, Type};

#[derive(Debug, Clone)]
pub struct PgWkbGeometry(pub Vec<u8>);

impl<'a> FromSql<'a> for PgWkbGeometry {
    fn from_sql(_ty: &Type, raw: &'a [u8]) -> Result<Self, Box<dyn std::error::Error + Sync + Send>> {
        Ok(PgWkbGeometry(raw.to_vec()))
    }
    fn accepts(ty: &Type) -> bool {
        ty.name() == "geometry"
    }
}

impl crate::myfrom::MyFrom<PgWkbGeometry> for parquet::data_type::ByteArray {
    fn my_from(v: PgWkbGeometry) -> Self {
        parquet::data_type::ByteArray::from(v.0)
    }
}
