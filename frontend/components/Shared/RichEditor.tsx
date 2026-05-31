"use client";

import { useEditor, EditorContent } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";
import Underline from "@tiptap/extension-underline";
import LinkExt from "@tiptap/extension-link";
import Placeholder from "@tiptap/extension-placeholder";
import { Table } from "@tiptap/extension-table";
import { TableRow } from "@tiptap/extension-table-row";
import { TableCell } from "@tiptap/extension-table-cell";
import { TableHeader } from "@tiptap/extension-table-header";
import TextAlign from "@tiptap/extension-text-align";
import Highlight from "@tiptap/extension-highlight";
import { useEffect } from "react";
import {
  Bold, Italic, Underline as UnderlineIcon, Strikethrough,
  Heading1, Heading2, Heading3,
  List, ListOrdered,
  AlignLeft, AlignCenter, AlignRight,
  Table as TableIcon,
  Link as LinkIcon,
  Code, FileCode,
  Minus, Undo2, Redo2,
  Highlighter,
} from "lucide-react";

interface RichEditorProps {
  content: string;
  onChange: (html: string) => void;
  placeholder?: string;
  minHeight?: number;
  disabled?: boolean;
}

// ── Toolbar button ─────────────────────────────────────────────────────────

function Btn({
  onClick,
  active,
  disabled,
  title,
  children,
}: {
  onClick: () => void;
  active?: boolean;
  disabled?: boolean;
  title?: string;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onMouseDown={(e) => { e.preventDefault(); onClick(); }}
      disabled={disabled}
      title={title}
      className={`rich-editor-btn${active ? " active" : ""}`}
    >
      {children}
    </button>
  );
}

const Sep = () => <span className="rich-editor-sep" />;

// ── Editor ─────────────────────────────────────────────────────────────────

export default function RichEditor({
  content,
  onChange,
  placeholder = "Escribe aquí...",
  minHeight = 200,
  disabled = false,
}: RichEditorProps) {
  const editor = useEditor({
    extensions: [
      StarterKit,
      Underline,
      Highlight,
      TextAlign.configure({ types: ["heading", "paragraph"] }),
      LinkExt.configure({ openOnClick: false, autolink: true }),
      Placeholder.configure({ placeholder }),
      Table.configure({ resizable: false }),
      TableRow,
      TableCell,
      TableHeader,
    ],
    content,
    editable: !disabled,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
  });

  // Sync content when it changes externally (e.g. loading an existing FAQ)
  useEffect(() => {
    if (!editor) return;
    const current = editor.getHTML();
    if (content !== current) {
      editor.commands.setContent(content);
    }
  }, [content, editor]);

  useEffect(() => {
    if (editor) editor.setEditable(!disabled);
  }, [disabled, editor]);

  if (!editor) return null;

  const addLink = () => {
    const url = window.prompt("URL del enlace (https://)");
    if (!url) return;
    editor.chain().focus().setLink({ href: url }).run();
  };

  const addTable = () => {
    editor.chain().focus().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run();
  };

  return (
    <div className="rich-editor-wrapper">
      {!disabled && (
        <div className="rich-editor-toolbar">
          {/* Text format */}
          <Btn onClick={() => editor.chain().focus().toggleBold().run()} active={editor.isActive("bold")} title="Negrita">
            <Bold size={13} strokeWidth={2.5} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleItalic().run()} active={editor.isActive("italic")} title="Cursiva">
            <Italic size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleUnderline().run()} active={editor.isActive("underline")} title="Subrayado">
            <UnderlineIcon size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleStrike().run()} active={editor.isActive("strike")} title="Tachado">
            <Strikethrough size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleHighlight().run()} active={editor.isActive("highlight")} title="Resaltar">
            <Highlighter size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Headings */}
          <Btn onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()} active={editor.isActive("heading", { level: 1 })} title="Título 1">
            <Heading1 size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()} active={editor.isActive("heading", { level: 2 })} title="Título 2">
            <Heading2 size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()} active={editor.isActive("heading", { level: 3 })} title="Título 3">
            <Heading3 size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Lists */}
          <Btn onClick={() => editor.chain().focus().toggleBulletList().run()} active={editor.isActive("bulletList")} title="Lista de viñetas">
            <List size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleOrderedList().run()} active={editor.isActive("orderedList")} title="Lista numerada">
            <ListOrdered size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Alignment */}
          <Btn onClick={() => editor.chain().focus().setTextAlign("left").run()} active={editor.isActive({ textAlign: "left" })} title="Alinear izquierda">
            <AlignLeft size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().setTextAlign("center").run()} active={editor.isActive({ textAlign: "center" })} title="Centrar">
            <AlignCenter size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().setTextAlign("right").run()} active={editor.isActive({ textAlign: "right" })} title="Alinear derecha">
            <AlignRight size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Code */}
          <Btn onClick={() => editor.chain().focus().toggleCode().run()} active={editor.isActive("code")} title="Código inline">
            <Code size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().toggleCodeBlock().run()} active={editor.isActive("codeBlock")} title="Bloque de código">
            <FileCode size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Link + Table + HR */}
          <Btn onClick={addLink} active={editor.isActive("link")} title="Insertar enlace">
            <LinkIcon size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={addTable} title="Insertar tabla">
            <TableIcon size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().setHorizontalRule().run()} title="Separador horizontal">
            <Minus size={13} strokeWidth={2} />
          </Btn>

          <Sep />

          {/* Undo / Redo */}
          <Btn onClick={() => editor.chain().focus().undo().run()} disabled={!editor.can().undo()} title="Deshacer">
            <Undo2 size={13} strokeWidth={2} />
          </Btn>
          <Btn onClick={() => editor.chain().focus().redo().run()} disabled={!editor.can().redo()} title="Rehacer">
            <Redo2 size={13} strokeWidth={2} />
          </Btn>
        </div>
      )}

      <EditorContent
        editor={editor}
        style={{ minHeight, cursor: disabled ? "default" : "text" }}
      />
    </div>
  );
}
