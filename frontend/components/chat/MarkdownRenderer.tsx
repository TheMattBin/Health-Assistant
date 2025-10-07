import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import styles from './MarkdownRenderer.module.css';

interface MarkdownRendererProps {
  content: string;
  isAI?: boolean;
}

export default function MarkdownRenderer({ content, isAI = false }: MarkdownRendererProps) {
  const components = {
    // Bold text
    strong: ({ children }: { children: React.ReactNode }) => (
      <strong className={styles.bold}>{children}</strong>
    ),

    // Italic text
    em: ({ children }: { children: React.ReactNode }) => (
      <em className={styles.italic}>{children}</em>
    ),

    // Headers
    h1: ({ children }: { children: React.ReactNode }) => (
      <h1 className={styles.h1}>{children}</h1>
    ),
    h2: ({ children }: { children: React.ReactNode }) => (
      <h2 className={styles.h2}>{children}</h2>
    ),
    h3: ({ children }: { children: React.ReactNode }) => (
      <h3 className={styles.h3}>{children}</h3>
    ),
    h4: ({ children }: { children: React.ReactNode }) => (
      <h4 className={styles.h4}>{children}</h4>
    ),

    // Lists
    ul: ({ children }: { children: React.ReactNode }) => (
      <ul className={styles.ul}>{children}</ul>
    ),
    ol: ({ children }: { children: React.ReactNode }) => (
      <ol className={styles.ol}>{children}</ol>
    ),
    li: ({ children }: { children: React.ReactNode }) => (
      <li className={styles.li}>{children}</li>
    ),

    // Code blocks and inline code
    code: ({ inline, children }: { inline?: boolean; children: React.ReactNode }) => {
      return inline ? (
        <code className={styles.inlineCode}>{children}</code>
      ) : (
        <pre className={styles.codeBlock}>
          <code>{children}</code>
        </pre>
      );
    },

    // Blockquotes
    blockquote: ({ children }: { children: React.ReactNode }) => (
      <blockquote className={styles.blockquote}>{children}</blockquote>
    ),

    // Links
    a: ({ href, children }: { href?: string; children: React.ReactNode }) => (
      <a href={href} className={styles.link} target="_blank" rel="noopener noreferrer">
        {children}
      </a>
    ),

    // Paragraphs
    p: ({ children }: { children: React.ReactNode }) => (
      <p className={styles.paragraph}>{children}</p>
    ),
  };

  return (
    <div className={`${styles.markdownContainer} ${isAI ? styles.aiMessage : styles.userMessage}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]} components={components}>
        {content}
      </ReactMarkdown>
    </div>
  );
}