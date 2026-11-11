use std::path::PathBuf;
use tauri::Manager;

fn database_path(app: &tauri::AppHandle) -> Result<PathBuf, String> {
    let mut path = app.path().app_data_dir().map_err(|e| e.to_string())?;
    std::fs::create_dir_all(&path).map_err(|e| e.to_string())?;
    path.push("lexi.sqlite3");
    Ok(path)
}

#[tauri::command]
fn initialize_database(app: tauri::AppHandle) -> Result<String, String> {
    let path = database_path(&app)?;
    let connection = rusqlite::Connection::open(&path).map_err(|e| e.to_string())?;
    connection.execute_batch(
        "PRAGMA journal_mode = WAL;
         PRAGMA foreign_keys = ON;
         CREATE TABLE IF NOT EXISTS schema_migrations (
             version INTEGER PRIMARY KEY,
             applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
         );
         CREATE TABLE IF NOT EXISTS cards (
             id TEXT PRIMARY KEY NOT NULL,
             card_type TEXT NOT NULL CHECK (card_type IN ('word', 'phrase', 'sentence')),
             english TEXT NOT NULL,
             translation TEXT,
             context TEXT,
             notes TEXT,
             created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
         );"
    ).map_err(|e| e.to_string())?;
    Ok(path.to_string_lossy().into_owned())
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![initialize_database])
        .setup(|app| {
            let handle = app.handle().clone();
            tauri::async_runtime::block_on(async move {
                initialize_database(handle).map(|_| ())
            })?;
            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running Lexi");
}
