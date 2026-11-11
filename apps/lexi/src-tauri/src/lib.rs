use rusqlite::{params, Connection};
use serde::Serialize;
use std::{path::PathBuf, time::{SystemTime, UNIX_EPOCH}};
use tauri::Manager;

fn now() -> i64 {
    SystemTime::now().duration_since(UNIX_EPOCH).unwrap_or_default().as_secs() as i64
}

fn database_path(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let mut path = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&path).map_err(|e| e.to_string())?;
    path.push("lexi.sqlite3");
    Ok(path)
}

fn connection(app: &tauri::AppHandle) -> Result<Connection, String> {
    let conn = Connection::open(database_path(app)?).map_err(|e| e.to_string())?;
    conn.execute_batch("PRAGMA journal_mode=WAL; PRAGMA foreign_keys=ON;").map_err(|e| e.to_string())?;
    Ok(conn)
}

fn migrate(conn: &Connection) -> Result<(), String> {
    conn.execute_batch(
        "CREATE TABLE IF NOT EXISTS schema_migrations (
            version INTEGER PRIMARY KEY,
            applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
         );
         CREATE TABLE IF NOT EXISTS cards (
            id TEXT PRIMARY KEY NOT NULL,
            card_type TEXT NOT NULL DEFAULT 'word' CHECK(card_type IN ('word','phrase','sentence')),
            english TEXT NOT NULL,
            translation TEXT,
            context TEXT,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            next_review_at INTEGER NOT NULL DEFAULT 0,
            review_count INTEGER NOT NULL DEFAULT 0
         );"
    ).map_err(|e| e.to_string())?;

    // Upgrade databases created by the initial scaffold.
    let mut stmt = conn.prepare("PRAGMA table_info(cards)").map_err(|e| e.to_string())?;
    let columns = stmt.query_map([], |row| row.get::<_, String>(1)).map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())?;
    if !columns.iter().any(|c| c == "next_review_at") {
        conn.execute("ALTER TABLE cards ADD COLUMN next_review_at INTEGER NOT NULL DEFAULT 0", []).map_err(|e| e.to_string())?;
    }
    if !columns.iter().any(|c| c == "review_count") {
        conn.execute("ALTER TABLE cards ADD COLUMN review_count INTEGER NOT NULL DEFAULT 0", []).map_err(|e| e.to_string())?;
    }
    Ok(())
}

#[derive(Serialize)]
#[serde(rename_all = "camelCase")]
struct Card {
    id: String,
    card_type: String,
    english: String,
    translation: String,
    context: String,
    notes: String,
    created_at: String,
    next_review_at: i64,
    review_count: i64,
}

fn map_card(row: &rusqlite::Row<'_>) -> rusqlite::Result<Card> {
    Ok(Card {
        id: row.get(0)?, card_type: row.get(1)?, english: row.get(2)?,
        translation: row.get::<_, Option<String>>(3)?.unwrap_or_default(),
        context: row.get::<_, Option<String>>(4)?.unwrap_or_default(),
        notes: row.get::<_, Option<String>>(5)?.unwrap_or_default(),
        created_at: row.get(6)?, next_review_at: row.get(7)?, review_count: row.get(8)?,
    })
}

const CARD_COLUMNS: &str = "id, card_type, english, translation, context, notes, created_at, next_review_at, review_count";

#[tauri::command]
fn initialize_database(app: tauri::AppHandle) -> Result<String, String> {
    let conn = connection(&app)?;
    migrate(&conn)?;
    Ok(database_path(&app)?.to_string_lossy().into_owned())
}

#[tauri::command]
fn list_cards(app: tauri::AppHandle, query: Option<String>, due_only: Option<bool>) -> Result<Vec<Card>, String> {
    let conn = connection(&app)?;
    migrate(&conn)?;
    let search = query.unwrap_or_default();
    let due = due_only.unwrap_or(false);
    let sql = format!(
        "SELECT {CARD_COLUMNS} FROM cards
         WHERE (?1 = '' OR english LIKE '%' || ?1 || '%' OR translation LIKE '%' || ?1 || '%' OR context LIKE '%' || ?1 || '%')
         AND (?2 = 0 OR next_review_at <= ?3)
         ORDER BY CASE WHEN next_review_at <= ?3 THEN 0 ELSE 1 END, created_at DESC"
    );
    let mut stmt = conn.prepare(&sql).map_err(|e| e.to_string())?;
    let rows = stmt.query_map(params![search, if due {1} else {0}, now()], map_card).map_err(|e| e.to_string())?;
    rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
}

#[tauri::command]
fn create_card(
    app: tauri::AppHandle, english: String, translation: String,
    context: String, notes: String, card_type: String
) -> Result<Card, String> {
    let english = english.trim().to_string();
    if english.is_empty() { return Err("Enter a word or phrase.".into()); }
    if !["word", "phrase", "sentence"].contains(&card_type.as_str()) {
        return Err("Invalid card type.".into());
    }
    let conn = connection(&app)?;
    migrate(&conn)?;
    let id = format!("{}-{}", now(), std::process::id());
    conn.execute(
        "INSERT INTO cards (id, card_type, english, translation, context, notes, next_review_at)
         VALUES (?1, ?2, ?3, ?4, ?5, ?6, ?7)",
        params![id, card_type, english, translation.trim(), context.trim(), notes.trim(), now()]
    ).map_err(|e| e.to_string())?;
    let sql = format!("SELECT {CARD_COLUMNS} FROM cards WHERE id=?1");
    conn.query_row(&sql, params![id], map_card).map_err(|e| e.to_string())
}

#[tauri::command]
fn delete_card(app: tauri::AppHandle, id: String) -> Result<(), String> {
    let conn = connection(&app)?;
    conn.execute("DELETE FROM cards WHERE id=?1", params![id]).map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn review_card(app: tauri::AppHandle, id: String, remembered: bool) -> Result<(), String> {
    let conn = connection(&app)?;
    let delay = if remembered { 24 * 60 * 60 } else { 10 * 60 };
    conn.execute(
        "UPDATE cards SET next_review_at=?1, review_count=review_count+1 WHERE id=?2",
        params![now() + delay, id]
    ).map_err(|e| e.to_string())?;
    Ok(())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![initialize_database, list_cards, create_card, delete_card, review_card])
        .setup(|app| {
            initialize_database(app.handle().clone()).map_err(std::io::Error::other)?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Lexi");
}
